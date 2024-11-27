from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from bs4 import BeautifulSoup
import random
import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from metaphone import doublemetaphone

from models.trademark_model import TrademarkData
from database import get_collection

router = APIRouter(prefix="/trademark", tags=["trademark"])
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_metaphone(name):
    return doublemetaphone(name)[0]

@router.get("/alldata")
async def get_all_data():
    try:
        collection = get_collection()
        data = collection.query(expr="")
        return {"message": "data received successfully", "data": data}
    except Exception as e:
        return {"error": str(e)}, 500

@router.get("/getdataontitle")
async def get_data_title(name: str = Query(..., description="The name to search for")):
    try:
        collection = get_collection()
        query_vector = model.encode(name).tolist()
        
        iterator = collection.search_iterator(
            data=[query_vector],
            anns_field="vector",
            param={"metric_type": "COSINE", "params": {"nprobe": 384}},
            limit=200,
            output_fields=["Title_Name", "Metaphone_Name", "Title_Code"],
        )
        
        results = []
        while True:
            result = iterator.next()
            if not result:
                iterator.close()
                break
            for hit in result:
                results.append(hit.to_dict())

        all_data = [{
            "Title_Code": r["entity"]["Title_Code"],
            "Title_Name": r["entity"]["Title_Name"],
            "Metaphone_Name": r["entity"]["Metaphone_Name"],
            "distance": r["distance"]
        } for r in results]

        df = pd.DataFrame(all_data)
        file_path = "results.csv"
        df.to_csv(file_path, index=False)
        return FileResponse(path=file_path, filename="results.csv", media_type="text/csv")

    except Exception as e:
        return {"error": str(e)}, 500

@router.post("/add")
async def insert_data(data: List[TrademarkData]):
    try:
        if not data:
            return {"error": "No data provided"}, 400
            
        collection = get_collection()
        for item in data:
            vector = [random.random() for _ in range(128)]
            item_dict = item.dict()
            item_dict["vector"] = vector
            collection.insert(item_dict)
            
        return {"message": "Data inserted successfully"}
    except Exception as e:
        return {"error": str(e)}, 500

@router.get("/deleteAllData")
def delete_all_data():
    try:
        collection = get_collection()
        collection.delete(expr="Auto_id >= 0")
        return {"message": "All data deleted successfully"}
    except Exception as e:
        return {"error": str(e)}, 500 