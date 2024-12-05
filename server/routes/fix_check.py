# from fastapi import APIRouter, Query
# import pandas as pd
# import csv
# from database import get_collection

# router = APIRouter(prefix="/fix", tags=["trademark"])

# @router.get("/space_nospace")
# async def get_all_data(name: str = Query(..., description="The name to search for")):
#     try:


#         allowed = is_not_in_list(name)
#         if allowed:
#             return {"Message":f"{name} is  allowed !"}
#         else:
#             return {"Message":f"{name} is not allowed !"}

#     except Exception as e:
#         return {"error": str(e.with_traceback())}, 500