from pydantic import BaseModel
from typing import List

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    category: str

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str
    category: str
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    products: List[ProductResponse]

class IngestResponse(BaseModel):
    message: str
    processed_products: int
    total_embeddings: int