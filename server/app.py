from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
