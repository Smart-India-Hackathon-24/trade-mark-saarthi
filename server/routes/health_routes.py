from fastapi import APIRouter

router = APIRouter()

@router.get("/", 
    summary="Root endpoint",
    description="Basic health check endpoint",
    response_description="Welcome message")
async def health_check():
    return {"message": "Hello From Backend"} 