from fastapi import APIRouter, Query
import pandas as pd
from database import get_collection

router = APIRouter(prefix="/fix", tags=["trademark"])

@router.get("/disallowed_fix")
async def get_all_data(name: str = Query(..., description="The name to search for")):
    try:
        disallowed_prefixes = ["HINDUSTAN", "INDIA"]
        disallowed_suffixes = ["TIMES", "DAY"]

        def is_valid_string(input_string, disallowed_prefixes, disallowed_suffixes):
            words = input_string.split()
            
            for word in words:
                for prefix in disallowed_prefixes:
                    if word.startswith(prefix):
                        return False
                
                for suffix in disallowed_suffixes:
                    if word.endswith(suffix):
                        return False
            
            return True

        allowed = is_valid_string(name, disallowed_prefixes, disallowed_suffixes)

        if allowed:
            return {"Message":f"{name} is  allowed !"}
        else:
            return {"Message":f"{name} is not allowed !"}

    except Exception as e:
        return {"error": str(e.with_traceback())}, 500