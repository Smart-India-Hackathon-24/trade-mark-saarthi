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
async def get_all_data(
    limit: int = Query(50, description="Number of records to return"),
    show_soundex: bool = Query(False, description="Show Soundex Name"),
    show_metaphone: bool = Query(False, description="Show Metaphone Name"), 
    show_double_metaphone_primary: bool = Query(False, description="Show Double Metaphone Primary"),
    show_double_metaphone_secondary: bool = Query(False, description="Show Double Metaphone Secondary"),
    show_nysiis: bool = Query(False, description="Show NYSIIS Name")
):
    try:
        collection = get_collection("Phonetic_Data")
        
        # Title_Name and Title_Code are always included
        output_fields = ["Title_Name", "Title_Code"]
        
        # Add optional fields based on query parameters
        if show_soundex:
            output_fields.append("Soundex_Name")
        if show_metaphone:
            output_fields.append("Metaphone_Name")
        if show_double_metaphone_primary:
            output_fields.append("Double_Metaphone_Primary")
        if show_double_metaphone_secondary:
            output_fields.append("Double_Metaphone_Secondary") 
        if show_nysiis:
            output_fields.append("NYSIIS_Name")

        data = collection.query(expr="", limit=limit, output_fields=output_fields, output_fields_exclude=["Auto_id"])
        return {"message": "data received successfully", "data": data}
    except Exception as e:
        return {"error": str(e)}, 500


@router.get("/getdataontitle")
async def get_data_title(name: str = Query(..., description="The name to search for")):
    try:
        collection = get_collection('All_Words_Count_List')
        print(name)
        print(get_metaphone(name))
        query_vector = model.encode(get_metaphone(name)).tolist()

        iterator = collection.search_iterator(
            data=[query_vector],
            anns_field="vector_of_metaphone",
            param={"metric_type": "COSINE", "params": {"nprobe": 384}},
            limit=200,
            output_fields=["Title_Name", "Metaphone_Name"],
        )

        results = []
        while True:
            result = iterator.next()
            if not result:
                iterator.close()
                break
            for hit in result:
                results.append(hit.to_dict())

        all_data = [
            {
                # "Title_Code": r["entity"]["Title_Code"],
                "Title_Name": r["entity"]["Title_Name"],
                "Metaphone_Name": r["entity"]["Metaphone_Name"],
                "distance": r["distance"],
            }
            for r in results
        ]

        df = pd.DataFrame(all_data)
        print(df)
        return df
        # file_path = "results.csv"
        # df.to_csv(file_path, index=False)
        # return FileResponse(
        #     path=file_path, filename="results.csv", media_type="text/csv"
        # )

    except Exception as e:
        return {"error": str(e)}, 500


@router.post("/add")
async def insert_data(data: List[TrademarkData]):
    try:
        if not data:
            return {"error": "No data provided"}, 400

        collection = get_collection('Phonetic_Data')
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
        collection = get_collection('Phonetic_Data')
        collection.delete(expr="Auto_id >= 0")
        return {"message": "All data deleted successfully"}
    except Exception as e:
        return {"error": str(e)}, 500
