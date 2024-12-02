from pydantic import BaseModel
from typing import List

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
                "periodity": "Monthly",
            }
        } 