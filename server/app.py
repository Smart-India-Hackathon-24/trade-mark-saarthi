from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import (
    API_TITLE, 
    API_DESCRIPTION, 
    API_VERSION, 
    ALLOWED_ORIGINS,
    PORT
)
from database import connect_db
from routes import health_routes, trademark_routes,simillarity_routes,searchresults
# ,semantic_routes

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)
from fastapi.responses import JSONResponse
from pymilvus import Collection, connections, FieldSchema, CollectionSchema, DataType
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import random
import json
from typing import List,Dict,Any
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from metaphone import doublemetaphone
import pandas as pd
from fastapi.responses import FileResponse


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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Connect to database
connect_db()

# Include routers
app.include_router(health_routes.router)
app.include_router(trademark_routes.router)
app.include_router(simillarity_routes.router)
app.include_router(searchresults.router)
# app.include_router(semantic_routes.router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
