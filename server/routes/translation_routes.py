from fastapi import APIRouter, Query
import pandas as pd
from sentence_transformers import SentenceTransformer
from pymilvus import AnnSearchRequest
from pymilvus import WeightedRanker
from fuzzywuzzy import fuzz
from phonetics import metaphone
import re
import json
from database import get_collection
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from ai4bharat.transliteration import XlitEngine
from googletrans import Translator
nltk.download('stopwords')
nltk.download('punkt_tab')

router = APIRouter(prefix="/translation", tags=["trademark"])
model = SentenceTransformer("all-MiniLM-L6-v2")
xlit = XlitEngine("hi", beam_width=10, rescore=True)
translator = Translator()

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


async def perform_hybrid_search(collection,reqs,output_fields,trans=0.8):
    processed_results = []
    rerank = WeightedRanker(trans)
    results = collection.hybrid_search(
    reqs,
    rerank,
    limit=200,
    output_fields=output_fields
    )
    for result in results[0]:
        processed_results.append({
            "distance": result.distance,
            "Title_Name": result.entity.get("Title_Name"),
            'Trans_Title_Sort_Name':result.entity.get('Trans_Title_Sort_Name')
        })
    return processed_results

async def hybrid_vector_search_for_count(name,trans):
    try:
        # global xlit
        collection=get_collection("Alphabetic_sort_2")
        # words = re.split(r'[ \-]', name)
        # trans_word_array=[]
        # for i in words:
        #     out = xlit.translit_word(i, topk=5)
        #     if (out and len(out['hi'])>0):
        #         try:
        #             translated_string1 = translator.translate(out['hi'][0], dest='en').text
        #             trans_word_array.append(translated_string1)
        #         except:
        #             print(name)
        #             print("Errror")
        #     else:
        #         print(out)
        #         print(len(out['hi']))
        #         translated_string1 = translator.translate(out['hi'][0], dest='en').text
        #         trans_word_array.append(translated_string1)
        # filtered_words = [word for word in trans_word_array if word.lower() not in stopwords.words('english')]
        # trans_sorted_sentence = sorted(filtered_words, key=str.lower)
        # trans_title_after_sort = ' '.join(trans_sorted_sentence)
        vector_for_trans=[model.encode(name).tolist()]
        search_param_1 = {
        "data": vector_for_trans, 
        "anns_field": "vector_of_trans_sorting", 
        "param": {
            "metric_type": "COSINE",
            "params": {"nprobe": 384}
        },
        "limit": 200,
        }
        reqs = [AnnSearchRequest(**search_param_1)]
        output_fields=["Title_Name",'Trans_Title_Sort_Name']
        final_result_df=await perform_hybrid_search(collection,reqs,output_fields,trans)
        df=pd.DataFrame(final_result_df)[:50]
        # df=df.sort_values(by=['distance'],ascending=False)[:60]
        # print(df)
        return df
        # return df.loc[df['Count']>100]
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500


@router.get("/sametitle")
async def same_title(name: str = Query(..., description="The name to search for"),trans: float = Query(..., description="The name to search for")):
    try:
        # LOKTANTRATIMES | LOKTANTRA TIMES | TIMES LOKTANTRA | TIMES OF LOKTANTRA | MAHARASHTRATIMES CITY
        # MAHARASHTRATIMESCITY -> Not working
        
        global xlit
        collection=get_collection("Alphabetic_sort_2")
        words = re.split(r'[ \-]', name)
        trans_word_array=[]
        for i in words:
            out = xlit.translit_word(i, topk=5)
            if (out and len(out['hi'])>0):
                try:
                    translated_string1 = translator.translate(out['hi'][0], dest='en').text
                    trans_word_array.append(translated_string1)
                except:
                    print(name)
                    print("Errror")
            else:
                print(out)
                print(len(out['hi']))
                translated_string1 = translator.translate(out['hi'][0], dest='en').text
                trans_word_array.append(translated_string1)
        filtered_words = [word for word in trans_word_array if word.lower() not in stopwords.words('english')]
        trans_sorted_sentence = sorted(filtered_words, key=str.lower)
        trans_title_after_sort = ' '.join(trans_sorted_sentence)
        print(trans_title_after_sort)
        # for i in range(2,11):
        result= await hybrid_vector_search_for_count(trans_title_after_sort.upper(),trans)
        # meta_dist=spell_check(get_metaphone(name.upper()),result['Metaphone_Name_After_Sort'])
        result['fuzzy'] = result['Trans_Title_Sort_Name'].apply(lambda x: fuzz.ratio(trans_title_after_sort.upper(), x))
        # result['Meta_Levensthein'] = meta_dist
        # lmax = result["Meta_Levensthein"].max()
        # result['Meta_Levensthein'] = lmax - result['Meta_Levensthein']
        # result = result.loc[
        #     (result['distance'] >= ((1.0 + float(0.3)) - 0.150)) &
        #     (result['fuzzy'] > 90)
        # ]
        # resultFDL = result.sort_values(
        #     by=['fuzzy','distance','Meta_Levensthein'], 
        #     ascending=[False,False,False])
        # resultFLD = result.sort_values(
        #     by=['fuzzy','Meta_Levensthein','distance'], 
        #     ascending=[False,False,False])
        # return {
        #         "message": f"Titles as same as {name}",
        #         "FDL":json.loads(resultFDL.to_json()),
        #         "FLD":json.loads(resultFLD.to_json())
        #     }
        return{
            "result":json.loads(result.to_json())
        }
        #     print(result)
        #     print("---------")
        # print("***************************************************************")
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/similartitles")
async def similar_title(name: str = Query(..., description="The name to search for"),trans: float = Query(..., description="The name to search for")):
    try:
        words = word_tokenize(name)
        filtered_words = [word for word in words if word.lower() not in stopwords.words('english')]
        sorted_sentence = sorted(filtered_words, key=str.lower)
        title_after_sort = ' '.join(sorted_sentence).upper()
        
        print(title_after_sort)
        print(get_metaphone(title_after_sort.upper()))
        result= await hybrid_vector_search_for_count(title_after_sort,trans)
        meta_dist=spell_check(get_metaphone(title_after_sort.upper()),result['Metaphone_Name_After_Sort'])
        result['fuzzy'] = result['Title_Name_After_Sort'].apply(lambda x: fuzz.ratio(title_after_sort.upper(), x))
        result['Meta_Levensthein'] = meta_dist
        lmax = result["Meta_Levensthein"].max()
        result['Meta_Levensthein'] = lmax - result['Meta_Levensthein']
        result = result.loc[
            (result['distance'] >= (0.6)) &
            (result['fuzzy'] >= 40)
        ]
        resultDFL = result.sort_values(
            by=['distance','fuzzy','Meta_Levensthein'], 
            ascending=[False,False,False])
        resultFDL = result.sort_values(
            by=['fuzzy','distance','Meta_Levensthein'], 
            ascending=[False,False,False])
        print(resultDFL)
        return {
                "message": f"Titles as same as {name}",
                "DFL":json.loads(resultDFL.to_json()),
                "FDL":json.loads(resultFDL.to_json()),
            }
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500    
    
@router.get("/similarsound")
async def similar_sound(name: str = Query(..., description="The name to search for"),trans: float = Query(..., description="The name to search for")):
    try:
        words = word_tokenize(name)
        filtered_words = [word for word in words if word.lower() not in stopwords.words('english')]
        sorted_sentence = sorted(filtered_words, key=str.lower)
        title_after_sort = ' '.join(sorted_sentence).upper()
        
        print(title_after_sort)
        print(get_metaphone(title_after_sort.upper()))
        result= await hybrid_vector_search_for_count(title_after_sort,trans)
        meta_dist=spell_check(get_metaphone(title_after_sort.upper()),result['Metaphone_Name_After_Sort'])
        result['fuzzy'] = result['Title_Name_After_Sort'].apply(lambda x: fuzz.ratio(title_after_sort.upper(), x))
        result['Meta_Levensthein'] = meta_dist
        lmax = result["Meta_Levensthein"].max()
        result['Meta_Levensthein'] = lmax - result['Meta_Levensthein']
        result = result.loc[
            (result['distance'] >= (0.65)) &
            (result['fuzzy'] >= 50)
        ]
        resultDFL = result.sort_values(
            by=['distance','fuzzy','Meta_Levensthein'], 
            ascending=[False,False,False])
        resultFLD = result.sort_values(
            by=['fuzzy','distance','Meta_Levensthein'], 
            ascending=[False,False,False])
        print(resultDFL)
        return {
                "message": f"Titles as same as {name}",
                "FDL":json.loads(resultDFL.to_json()),
                "FLD":json.loads(resultFLD.to_json())
            }
    except Exception as e:
            return {"error": str(e.with_traceback())}, 500
