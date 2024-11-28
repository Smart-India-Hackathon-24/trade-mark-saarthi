from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymilvus import Collection, connections, FieldSchema, CollectionSchema, DataType
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import random
import json
from typing import List
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from metaphone import doublemetaphone
import pandas as pd
from fastapi.responses import FileResponse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np


load_dotenv()

# Connect to Zilliz Cloud
connections.connect(
    alias="default",
    uri=os.getenv("ZILLIZ_URI"),
    token=os.getenv("ZILLIZ_TOKEN")    
)

# Configure allowed origins
origins = [
    "http://localhost:3000",    # React default port
    "http://localhost:8080",    # Common frontend port
    # Add other allowed origins as needed
]

app = FastAPI()

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Define a Pydantic model for the data structure
class TrademarkData(BaseModel):
    title_code: str
    title_name: str
    hindi_title: str
    register_serial_no: str
    regn_no: str
    owner_name: str
    state: str
    publication_city_district: str
    periodity: str
    # vector: List[float] 




# collection_name = "TradeMark_Sarthi"
# collection = Collection(name=collection_name)
auto_id_field = FieldSchema(name="Auto_id", dtype=DataType.INT64, is_primary=True, auto_id=True)
vector_field = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384)
title_code_field = FieldSchema(name="Title_Code", dtype=DataType.VARCHAR, max_length=200)
title_name_field = FieldSchema(name="Title_Name", dtype=DataType.VARCHAR, max_length=200)
soundex_name_field = FieldSchema(name="Soundex_Name", dtype=DataType.VARCHAR, max_length=200)
metaphone_name_field = FieldSchema(name="Metaphone_Name", dtype=DataType.VARCHAR, max_length=200)
double_metaphone_primary_field = FieldSchema(name="Double_Metaphone_Primary", dtype=DataType.VARCHAR, max_length=200)
double_metaphone_secondary_field = FieldSchema(name="Double_Metaphone_Secondary", dtype=DataType.VARCHAR, max_length=200)
nysiis_name_field = FieldSchema(name="NYSIIS_Name", dtype=DataType.VARCHAR, max_length=200)


schema = CollectionSchema(
    fields=[
        auto_id_field,
        vector_field,
        title_code_field,
        title_name_field,
        soundex_name_field,
        metaphone_name_field,
        double_metaphone_primary_field,
        double_metaphone_secondary_field,
        nysiis_name_field
    ],
    description="Collection for title information with vector embeddings and phonetic codes."
)

collection_name = "Simple_Embeddings"
collection=''
try:
    collection = Collection(name=collection_name)  
    collection.load()
    print("Collection exists.")
except Exception as e:
    collection = Collection(name=collection_name, schema=schema) 
    print("Collection created.")


if connections.has_connection("default"):
    print("Connection successful!")
else:
    print("Failed to connect.")



@app.get('/extract-data')
def extract_data():
    with open('../dataset/final.html', 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    data = []
    table = soup.find('table')
    for row in table.find_all('tr')[1:]: 
        cols = row.find_all('td')
        if cols: 
            entry = {
                "title_code": cols[0].get_text(strip=True),
                "title_name": cols[1].get_text(strip=True),
                "hindi_title": cols[2].get_text(strip=True),
                "register_serial_no": cols[3].get_text(strip=True),
                "regn_no": cols[4].get_text(strip=True),
                "owner_name": cols[5].get_text(strip=True),
                "state": cols[6].get_text(strip=True),
                "publication_city_district": cols[7].get_text(strip=True),
                "periodity": cols[8].get_text(strip=True),
                "vector":[random.random() for _ in range(128)],  #dummy_vectors
            }
            data.append(entry)

    # if you want to add data into db then please uncomment below two lines
    # if data:
    #     collection.insert(data)
    #     dummy_vectors = [[random.random() for _ in range(128)] for _ in range(len(data))]

    return {"message":"data extracted successfully","data":data}


@app.get("/trademark/alldata")
async def get_all_data():
    try:
        # output_fields = [field.name for field in collection.schema.fields if field.name!='vector']
        # output_fields = [field.name for field in collection.schema.fields if field.name != 'vector']
        data = collection.query(expr="")
        return {"message": "data received successfully", "data": data}
    except Exception as e:
        return {"error": str(e)}, 500  # Return error message


def calculate_similarity(query_vector, stored_vector):
    return 1 - cosine(query_vector, stored_vector)

def get_metaphone(name):
    return doublemetaphone(name)[0]


@app.get("/trademark/querydata")
async def get_query_data():
    try:
        query_metaphone = get_metaphone("SAMPURNA JAGRAN")
        query_vector = model.encode(query_metaphone).tolist()
        # vector_results = []
        # output_fields = [field.name for field in collection.schema.fields]
        # data = collection.query(expr="",output_fields=output_fields,limit=5)
        # # print(data)
        # for row in data:
        #     print("roowwwwwwws",row)
        #     print(row['vector'])
        #     similarity = calculate_similarity(query_vector, row['vector'])
        #     vector_results.append((row, similarity))

        # # Sort the vector results by similarity score
        # vector_results.sort(key=lambda x: x[1], reverse=True)
        # result=[row for row, _ in vector_results[:5]]
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        # results = collection.query(
        #     # data=[query_vector],
        #     # anns_field="vector",
        #     # param=search_params,
        #     limit=5,
        #     expr=f"Metaphone_Name=='{query_metaphone}'",
        #     output_fields=["Metaphone_Name","Title_Code","Title_Name"]
        # )
        results=collection.search(
            data=[query_vector],
            anns_field="vector",
            param={"metric_type": "COSINE", "params": {"nprobe": 384}},
            limit=200,
            # expr=f"Metaphone_Name=='{query_metaphone}'",
            output_fields=["Metaphone_Name","Title_Code","Title_Name"]
        )
        with open("viren1.txt", "w", encoding="utf-8") as f:
            f.write(results)
        print(results)
        print("viren111111111111111111111111111111111111111111111111111111111111111116")
        # with open("viren1.txt", "w+", encoding="utf-8") as f:
        #     f.write("123345")
        #     for result in output:
        #         # Convert each result dictionary to a string and write to the file
        #         f.write(f"Title Code: {result['Title_Code']}\n")
        #         f.write(f"Title Name: {result['Title_Name']}\n")
        #         f.write(f"Metaphone Name: {result['Metaphone_Name']}\n")
        #         f.write(f"Score: {result['score']}\n")
        #         f.write("\n")
        # output=parsed_result(results)
        # print(output)
        return results
        return {"message": "data received successfully", "data": results}
    except Exception as e:
        return {"error": str(e)}, 500  # Return error message


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
        suggestions.append((correct_word, distance))

    suggestions.sort(key=lambda x: x[1])
    return suggestions[:100]

def generate_iterator(query_vector,param,limit,output_fields):
    results=[]
    iterator=collection.search_iterator(
            data=[query_vector],
            anns_field="vector",
            param={"metric_type": "COSINE", "params": {"nprobe": 384,}},
            limit=limit,
            # expr=f"Metaphone_Name=='{query_metaphone}'",
            output_fields=["Title_Name","Metaphone_Name","Title_Code"]
        )
    while True:
        result = iterator.next()
        if not result:
            iterator.close()
            break
        for hit in result:
            results.append(hit.to_dict())
    return results

@app.get("/trademark/getdataontitle")
async def get_data_title(name: str = Query(..., description="The name to search for")):
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        name=name.upper()
        all_data=[]
        # results = []
        query_vector = model.encode(name).tolist()
        results=generate_iterator([query_vector],{"metric_type": "COSINE", "params": {"nprobe": 384,}},200,["Title_Name","Metaphone_Name","Title_Code"])

        for i in range(len(results)):
            all_data.append({
                "Title_Code":results[i]['entity']['Title_Code'],
                "Title_Name":results[i]['entity']['Title_Name'],
                "Metaphone_Name":results[i]['entity']['Metaphone_Name'],
                "distance":results[i]['distance']
            })
        df=pd.DataFrame(all_data)
        suggestions = spell_check(name,df['Title_Name'])
        print(f"Top 10 suggestions for '{name}':")
        for word, distance in suggestions:
            print(f"{word} (Distance: {distance})")
        # file_path = "results.csv"
        # df.to_csv(file_path, index=False)
        # return FileResponse(
        #     path=file_path,
        #     filename="results.csv",
        #     media_type="text/csv"
        # )
            
    except Exception as e:
        return {"error": str(e)}, 500
    # finally:
    #     # Ensure the temporary file is deleted after the response
    #     if os.path.exists("results.csv"):
    #         os.remove("results.csv")

@app.get("/trademark/wordcount")
async def count_words():
    try:
       text2=""
       iterator = collection.query_iterator(
            expr="",
            output_fields=["Title_Name"]
        )
       print(iterator)
       results = []
       while True:
           result=iterator.next()
           if not result:
               iterator.close()
               break
           df=pd.DataFrame(result)
           text2 += " ".join(title for title in df['Title_Name'])
        #    print(text2)
           results+=result
       words = text2.split()
       total = Counter(words)
       title_name=np.array(list(total.keys()))
       word_count = np.array(list(total.values()), dtype=np.int32)
       count_df=pd.DataFrame({'Title_Name':title_name,'Word_Count':word_count})
       count_df = count_df.sort_values(by="Word_Count", ascending=False).reset_index(drop=True)
       
    #    word_cloud2.to_file("word_cloud.png")
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/trademark/deleteAllData")
def delete_all_data():
    try:
        global collection
        collection.delete(expr="Auto_id >= 0")
        
    except Exception as e:
        return {"error": str(e)}, 500 
        

@app.post("/trademark/add")
async def insert_data(data:List[TrademarkData]):
    try:
        print(data)
        if not data:
            return {"error": "No data provided"}, 400
        for item in data:
            # Generate a random vector of 128 float values
            vector = [random.random() for _ in range(128)]
            # Convert the Pydantic model to a dictionary and add the vector
            item_dict = item.dict()
            item_dict['vector'] = vector
            
            # Insert the item into the collection
            collection.insert(item_dict)
        # print(data)
        return {"message": "Data inserted successfully"},200
    except Exception as e:
        print("ERROR",e)
        return {"error": str(e)}, 500 

@app.get("/")
async def getApi():
    return "Hello"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # Run server using: python app.py
    # Or using uvicorn directly: uvicorn app:app --host 0.0.0.0 --port 8000 --reload



# https://medium.com/@zilliz_learn/getting-started-with-a-milvus-connection-9e11a24e0a44
# https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/
# Define Collection Schema
# field1 = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True)
# field2 = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)
# schema = CollectionSchema(fields=[field1, field2], description="Example collection")
