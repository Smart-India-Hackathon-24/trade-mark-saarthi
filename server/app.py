from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymilvus import Collection, connections
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup


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

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)



collection_name = "TradeMark_Sarthi"
collection = Collection(name=collection_name)

if connections.has_connection("default"):
    print("Connection successful!")
else:
    print("Failed to connect.")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get('/extract-data')
def extract_data():
    # Load and parse the HTML file
    with open('../dataset/final.html', 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Extract data (modify this according to your HTML structure)
    data = []
    table = soup.find('table')
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        if cols:  # Ensure there are columns
            entry = {
                "title_code": cols[0].get_text(strip=True),
                "title_name": cols[1].get_text(strip=True),
                "hindi_title": cols[2].get_text(strip=True),
                "register_serial_no": cols[3].get_text(strip=True),
                "regn_no": cols[4].get_text(strip=True),
                "owner_name": cols[5].get_text(strip=True),
                "state": cols[6].get_text(strip=True),
                "publication_city_district": cols[7].get_text(strip=True),
                "periodity": cols[8].get_text(strip=True),
            }
            data.append(entry)
    # for item in soup.find_all('your-target-element'):
    #     data.append(item.get_text())
    # print(data)

    return {"message":"data extracted successfully","data":data}

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



# https://medium.com/@zilliz_learn/getting-started-with-a-milvus-connection-9e11a24e0a44
# https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/
# Define Collection Schema
# field1 = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True)
# field2 = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)
# schema = CollectionSchema(fields=[field1, field2], description="Example collection")
