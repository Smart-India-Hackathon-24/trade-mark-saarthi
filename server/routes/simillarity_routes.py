from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from utils.similarity_utils import (
    hybrid_vector_search_for_count,
    process_common_prefix_suffix
)

router = APIRouter(prefix="/similarity", tags=["trademark"])

@router.get("/titcommonpresuf")
async def get_all_data():
    try:
        await process_common_prefix_suffix()
        return {"message": "Files created successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/similarsoundingnames")
async def similar_sounding_names():
    try:
        # Implement this endpoint if needed
        pass
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/commonprefixsuffix")
async def similar_sounding_names(name: str = Query(..., description="The name to search for")):
    try:
        total_count = 0
        matches_found = []
        
        for n in name.split():
            result = await hybrid_vector_search_for_count(n)
            result = result.loc[result['distance'] > 0.80]
            
            if result.shape[0] > 0:
                word_count = sum(result['Count'])
                total_count += word_count
                matches_found.append(
                    f"The word '{n}' or similar matches with {(word_count * 100) / 10000:.2f}% of total names."
                )
            else:
                matches_found.append(f"No match found for the word '{n}'.")

        if total_count > 0:
            return {
                "message": f"The name '{name}' is very common in the database.",
                "details": matches_found,
            }
        elif total_count == 0:
            return {"message": f"The name '{name}' has no common words in the database."}
        else:
            return {
                "message": f"Results for the name '{name}':",
                "details": matches_found,
            }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )