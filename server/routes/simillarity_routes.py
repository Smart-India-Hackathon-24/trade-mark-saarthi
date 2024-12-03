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

from models.trademark_model import TrademarkData
from database import get_collection

router = APIRouter(prefix="/similarity", tags=["trademark"])
model = SentenceTransformer("all-MiniLM-L6-v2")

@router.get("/titcommonpresuf")
async def get_all_data():
    # Identify the titles that have common prefix and suffix eg. THE,INDIA,SAMACHAR,NEWS
    try:
        results = []
        collection=get_collection("Simple_Embeddings")
        iterator = collection.query_iterator(
        expr="",
        output_fields=["Title_Name"]
        )
        print(iterator)
        while True:
            result=iterator.next()
            if not result:
                iterator.close()
                break
            results+=result
        name_df=pd.DataFrame(results)
        word_count_df=pd.read_csv('../dataFiles/word_counts.csv')
        stop_words=word_count_df.loc[word_count_df['Word_Count']>100]
        stop_words=stop_words['Title_Name'].to_list()
        prefix_matches = name_df['Title_Name'].str.split().str[0].isin(stop_words)
        suffix_matches = name_df['Title_Name'].str.split().str[-1].isin(stop_words)
        titlesWithCommonPreSuff = name_df.loc[prefix_matches | suffix_matches]
        titleWithNonCommon=name_df.loc[~name_df['Title_Name'].isin(titlesWithCommonPreSuff['Title_Name'])]
        
        titlesWithCommonPreSuff.to_csv("../dataFiles/titlesWithCommonPreSuff.csv", index=False)
        titleWithNonCommon.to_csv("../dataFiles/titlesWithNonCommon.csv",index=False)
        return {"Message":"File created succesfully"}
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500
    
    
@router.get("/similarsoundingnames")
async def similar_sounding_names():
    try:
        pass
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500
    
def get_metaphone(name):
    return doublemetaphone(name)[0]
    
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

async def hybrid_vector_search_for_count(name):
    try:
        collection=get_collection("All_Words_Count_List")
        nameVector=[model.encode(name).tolist()]
        metaphoneVector=[model.encode(get_metaphone(name)).tolist()]
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
        final_result_df=await perform_hybrid_search(collection,reqs,output_fields,0.8,0.2,)
        df=pd.DataFrame(final_result_df)
        df=df.sort_values(by=['distance',"Count"],ascending=False)[:50]
        return df.loc[df['Count']>100]
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500

@router.get("/commonprefixsuffix")
async def similar_sounding_names(name: str = Query(..., description="The name to search for")):
    try:
        total_count = 0
        matches_found = []
        for n in name.split():
            result= await hybrid_vector_search_for_count(n)
            result=result.loc[result['distance']>0.80]
            if result.shape[0] > 0:
                word_count = sum(result['Count'])
                total_count += word_count
                matches_found.append(f"The word '{n}' or similar matches with {(word_count * 100) / 10000:.2f}% of total names.")
            else:
                matches_found.append(f"No match found for the word '{n}'.")
        if total_count > 0:  # Example threshold for a "very common" name
            return {
                "message": f"The name '{name}' is very common in the database.",
                "details": matches_found,
                "result":result
            }
        elif total_count == 0:
            return {"message": f"The name '{name}' has no common words in the database."}
        else:
            return {
                "message": f"Results for the name '{name}':",
                "details": matches_found,
            }
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500