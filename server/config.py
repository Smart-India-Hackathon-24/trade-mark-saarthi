from dotenv import load_dotenv
import os

load_dotenv()

# API Configuration
API_TITLE = "Trademark Sarthi API"
API_DESCRIPTION = "API for trademark search and management"
API_VERSION = "1.0.0"

# Database Configuration
ZILLIZ_URI = os.getenv("ZILLIZ_URI")
ZILLIZ_TOKEN = os.getenv("ZILLIZ_TOKEN")

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://trade-mark-saarthi.onrender.com",
    "https://trade-mark-saarthi-production.up.railway.app",
]

# Server Configuration
PORT = int(os.getenv("PORT", 10000)) 