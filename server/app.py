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
from routes import health_routes, trademark_routes, simillarity_routes, combination, fix_check

# Initialize FastAPI app only once
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv()

# Connect to Zilliz Cloud
from pymilvus import connections
connections.connect(
    alias="default",
    uri=os.getenv("ZILLIZ_URI"),
    token=os.getenv("ZILLIZ_TOKEN")    
)

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
app.include_router(combination.router)
app.include_router(fix_check.router)
# app.include_router(semantic_routes.router)
if __name__ == "__main__":
    # For local development
    uvicorn.run(app, host="0.0.0.0", port=PORT)
else:
    # For production
    # This is important for Railway deployment
    port = int(os.getenv("PORT", PORT))
    host = os.getenv("HOST", "0.0.0.0")
