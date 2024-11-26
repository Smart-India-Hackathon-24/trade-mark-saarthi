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


load_dotenv()

# Connect to Zilliz Cloud
try:
    # Check if environment variables are set
    zilliz_uri = os.getenv("ZILLIZ_URI")
    zilliz_token = os.getenv("ZILLIZ_TOKEN")
    
    if not zilliz_uri:
        raise ValueError("ZILLIZ_URI environment variable is not set")
    if not zilliz_token:
        raise ValueError("ZILLIZ_TOKEN environment variable is not set")
        
    connections.connect(
        alias="default",
        uri=zilliz_uri,
        token=zilliz_token
    )
    print("Successfully connected to Zilliz Cloud")
except Exception as e:
    print(f"Failed to connect to Zilliz Cloud: {str(e)}")
    # You may want to exit the application or handle the error appropriately
    raise

# Configure allowed origins
origins = [
    "http://localhost:3000",    # React default port
    "http://localhost:8080",    # Common frontend port
    "https://trademark-sarthi.vercel.app",  # Vercel deployment
    "*"  # Allow all origins in development
]

app = FastAPI(
    title="Trademark Sarthi API",
    description="API for trademark search and management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

    class Config:
        schema_extra = {
            "example": {
                "title_code": "ABC123",
                "title_name": "Sample Trademark",
                "hindi_title": "नमूना ट्रेडमार्क",
                "register_serial_no": "REG123",
                "regn_no": "456",
                "owner_name": "John Doe",
                "state": "Maharashtra",
                "publication_city_district": "Mumbai",
                "periodity": "Monthly"
            }
        }
