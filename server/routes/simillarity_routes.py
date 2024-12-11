from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
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
from fuzzywuzzy import fuzz
from phonetics import metaphone

import json
from models.trademark_model import TrademarkData
from database import get_collection
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
# nltk.download('stopwords')
# nltk.download('punkt_tab')

router = APIRouter(prefix="/similarity", tags=["trademark"])
model = SentenceTransformer("all-MiniLM-L6-v2")

@router.get("/titcommonpresuf")
async def get_all_data():
    # Identify the titles that have common prefix and suffix eg. THE,INDIA,SAMACHAR,NEWS
    try:
        results = []
        collection=get_collection("Phonetic_Data")
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
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/similarsoundingnames")
async def similar_sounding_names():
    try:
        # Implement this endpoint if needed
        pass
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500
    
def get_metaphone(name):
    # return doublemetaphone(name)[0]
    return metaphone(name)


def wagner_fischer(s1, s2):
    len_s1, len_s2 = len(s1), len(s2)
    if len_s1 > len_s2:
        s1, s2 = s2, s1
        len_s1, len_s2 = len_s2, len_s1

    current_row = range(len_s1 + 1)
    for i in range(1, len_s2 + 1):
        previous_row, current_row = current_row, [i] + [0] * len_s1
        for j in range(1, len_s1 + 1):
            add, delete, change = previous_row[j] + 1, current_row[j-1] + 1, previous_row[j-1]
            if s1[j-1] != s2[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[len_s1]

def spell_check(word, dictionary):
    suggestions = []

    for correct_word in dictionary:
        distance = wagner_fischer(word, correct_word)
        suggestions.append(distance)

    # suggestions.sort(key=lambda x: x[1])
    return suggestions
    
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

async def hybrid_vector_search_for_count(name,title,meta):
    try:
        collection=get_collection("Phonetic_Data")
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
        output_fields=["Metaphone_Name","Title_Name"]
        final_result_df=await perform_hybrid_search(collection,reqs,output_fields,title,meta,)
        df=pd.DataFrame(final_result_df)
        df=df.sort_values(by=['distance'],ascending=False)[:60]
        return df
        # return df.loc[df['Count']>100]
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500

@router.get("/commonprefixsuffix")
async def similar_sounding_names(name: str = Query(..., description="The name to search for"),title: float = Query(..., description="The name to search for"),meta: float = Query(..., description="The name to search for")):
    try:
        total_count = 0
        matches_found = []
        words = word_tokenize(name)
        title_sorted=word_tokenize(name)
        filtered_words = [word for word in words if word.lower() not in stopwords.words('english')]
        sorted_sentence = sorted(filtered_words, key=str.lower)
        title_after_sort = ' '.join(sorted_sentence)
        
        for n in name.split():
            print(n)
            print(get_metaphone(title_after_sort.upper()))
            n=n.upper()
            result= await hybrid_vector_search_for_count(name.upper(),title,meta)
            title_name_dist = spell_check(name,result['Title_Name'])
            meta_dist=spell_check(get_metaphone(name),result['Metaphone_Name'])
            result['fuzzy'] = result['Title_Name'].apply(lambda x: fuzz.ratio(name.upper(), x))
            result['Meta_Levensthein'] = meta_dist
            result = result.sort_values(
                by=['fuzzy','distance'], 
                ascending=[False,False])
            print(result)
            result=result.loc[result['distance']>0.80]
            # return result
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
        #         "result":json.loads(result.to_json())
        #     }
        # elif total_count == 0:
        #     return {"message": f"The name '{name}' has no common words in the database."}
        # else:
        #     return {
        #         "message": f"Results for the name '{name}':",
        #         "details": matches_found,
        #     }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )