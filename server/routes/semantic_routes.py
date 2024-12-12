from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from bs4 import BeautifulSoup
import random
import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from metaphone import doublemetaphone
from pymilvus import AnnSearchRequest
from pymilvus import WeightedRanker
from database import get_collection

router = APIRouter(prefix="/semantic", tags=["trademark"])
model = SentenceTransformer("all-MiniLM-L6-v2")

from ai4bharat.transliteration import XlitEngine
e = XlitEngine("hi", beam_width=4, rescore=True, src_script_type="en")

async def perform_hybrid_search(collection,reqs,output_fields,name=0.8,meta=0.2):
    processed_results = []
    rerank = WeightedRanker(name, meta)
    results = collection.hybrid_search(
    reqs,
    rerank,
    limit=200,
    output_fields=output_fields
    )
    for result in results[0]:
        processed_results.append({
            "distance": result.distance,
            "Metaphone_Name": result.entity.get("Metaphone_Name"),
            "Title_Name": result.entity.get("Title_Name"),
            "Count":result.entity.get("Count")
        })
    return processed_results

async def hybrid_vector_search_for_count(name,title_thresh=0.2,hindi_thresh=0.8):
    try:
        collection=get_collection("All_Words_Count_List")
        nameVector=[model.encode(name).tolist()]
        metaphoneVector=[model.encode(e.translit_word(name, topk=1)['hi'][0]).tolist()]
        search_param_1 = {
        "data": nameVector, 
        "anns_field": "vector_of_name", 
        "param": {
            "metric_type": "COSINE", 
            "params": {"nprobe": 384}
        },
        "limit": 200,
        }
        search_param_2 = {
        "data": metaphoneVector, 
        "anns_field": "vector_of_metaphone", 
        "param": {
            "metric_type": "COSINE",
            "params": {"nprobe": 384}
        },
        "limit": 200,
        }
        reqs = [AnnSearchRequest(**search_param_1), AnnSearchRequest(**search_param_2)]
        output_fields=["Metaphone_Name","Title_Name",'Count']
        final_result_df=await perform_hybrid_search(collection,reqs,output_fields,title_thresh,hindi_thresh,)
        df=pd.DataFrame(final_result_df)
        # df=df.sort_values(by=['distance',"Count"],ascending=False)[:50]
        return df
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500

@router.get('/gethindinames')
async def similar_sounding_names(name: str = Query(..., description="The name to search for"),title_thresh: float = Query(50, description="Threshold for title_name"),hindi_thresh: float = Query(50, description="Threshhold for hindi title")):
    try:
        total_count = 0
        matches_found = []
        # for n in name.split():
        result= await hybrid_vector_search_for_count(name,title_thresh,hindi_thresh)
        return result
        #     if result.shape[0] > 0:
        #         word_count = sum(result['Count'])
        #         total_count += word_count
        #         matches_found.append(f"The word '{n}' or similar matches with {(word_count * 100) / 10000:.2f}% of total names.")
        #     else:
        #         matches_found.append(f"No match found for the word '{n}'.")
        # if total_count > 0:  # Example threshold for a "very common" name
        #     return {
        #         "message": f"The name '{name}' is very common in the database.",
        #         "details": matches_found,
        #     }
        # elif total_count == 0:
        #     return {"message": f"The name '{name}' has no common words in the database."}
        # else:
        #     return {
        #         "message": f"Results for the name '{name}':",
        #         "details": matches_found,
        #     }
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500