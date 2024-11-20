from fastapi import FastAPI
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


fields = [
    FieldSchema(name="title_code", dtype=DataType.VARCHAR, max_length=50, is_primary=True),
    FieldSchema(name="title_name", dtype=DataType.VARCHAR, max_length=255),
    FieldSchema(name="hindi_title", dtype=DataType.VARCHAR, max_length=255),
    FieldSchema(name="register_serial_no", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="regn_no", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="owner_name", dtype=DataType.VARCHAR, max_length=255),
    FieldSchema(name="state", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="publication_city_district", dtype=DataType.VARCHAR, max_length=255),
    FieldSchema(name="periodity", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),  # Vector field with dimension 128
]

collection_schema = CollectionSchema(fields, description="Title Registration Data")

collection_name = "TradeMark_Viren"
collection=''
try:
    collection = Collection(name=collection_name)  
    collection.load()
    print("Collection exists.")
except Exception as e:
    collection = Collection(name=collection_name, schema=collection_schema) 
    print("Collection created.")


if connections.has_connection("default"):
    print("Connection successful!")
else:
    print("Failed to connect.")



@app.get('/extract-data')
def extract_data():
    with open('dataset\Final.html', 'r') as file:
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
    if data:
        collection.insert(data)
        # dummy_vectors = [[random.random() for _ in range(128)] for _ in range(len(data))]

    return {"message":"data extracted successfully","data":data}


@app.get("/trademark/alldata")
async def get_all_data():
    try:
        # output_fields = [field.name for field in collection.schema.fields if field.name!='vector']
        output_fields = [field.name for field in collection.schema.fields if field.name != 'vector']
        data = collection.query(expr="", output_fields=output_fields,limit=10)
        return {"message": "data received successfully", "data": data}
    except Exception as e:
        return {"error": str(e)}, 500  # Return error message


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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    try:
        return {"message": "Welcome to the API"}
    except Exception as e:
        # Return proper FastAPI response with status code
        return {"error": str(e)}, 500


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
