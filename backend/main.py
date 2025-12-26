from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from langchain_text_splitters import RecursiveCharacterTextSplitter
import httpx
import os
from typing import List
from contextlib import asynccontextmanager
from pathlib import Path

from database import get_db, init_db
from models import Product, ProductEmbedding
from schemas import (
    ProductCreate, ProductResponse, 
    ChatRequest, ChatResponse, IngestResponse
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... Creating database tables")
    try:
        await init_db()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("App will continue without database - some features may not work")
    yield
    print("Shutting down...")

app = FastAPI(title="AI Shopping Expert", version="1.0.0", lifespan=lifespan)

# Mount static files for production
static_path = os.path.join(os.getcwd(), "static")
if os.path.exists(static_path):
    # Mount the entire static directory to serve all assets
    app.mount("/static", StaticFiles(directory=static_path, html=True), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3-8b-8192")

# Simple fallback embeddings using HuggingFace Inference API
import hashlib
import json
async def get_embedding(text: str) -> List[float]:
    try:
        # Use HuggingFace Inference API to save memory
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/pipeline/feature-extraction/{EMBEDDING_MODEL}",
                headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
                json={"inputs": text},
                timeout=30.0
            )
            if response.status_code == 200:
                embedding = response.json()
                # Handle different response formats
                if isinstance(embedding, list) and len(embedding) > 0:
                    if isinstance(embedding[0], list):
                        return embedding[0][:384]  # Take first 384 dimensions
                    return embedding[:384]
    except Exception as e:
        print(f"HuggingFace API failed: {e}")
    
    # Fallback to hash-based embedding if API fails
    text_hash = hashlib.sha256(text.lower().encode()).hexdigest()
    embedding = []
    for i in range(0, min(len(text_hash), 96), 2):
        embedding.append(int(text_hash[i:i+2], 16) / 255.0)
    
    while len(embedding) < 384:
        embedding.extend(embedding[:min(len(embedding), 384-len(embedding))])
    
    return embedding[:384]

# Intent Router
async def classify_intent(query: str) -> str:
    intent_prompt = "Classify this user message as either 'PRODUCT_QUERY' or 'GENERAL_QUERY'. PRODUCT_QUERY means they want to find/buy products. GENERAL_QUERY means greetings, questions about you, or general chat. Reply with only one word: PRODUCT_QUERY or GENERAL_QUERY"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": intent_prompt},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 10
            },
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        return "PRODUCT_QUERY"  # Default fallback

# Updated system prompt
async def generate_chat_response(query: str, context: str) -> str:
    system_prompt = """You are 'NeuSearch AI', a professional, concise, and smart Shopping Assistant for an e-commerce store. 

Your behavior must follow these strict rules:

1. INTENT RECOGNITION:
   - If the user greets you (e.g., 'Hi', 'Hello'), reply warmly and ask how you can help them find a product today.
   - If the user asks general questions (e.g., 'Who are you?', 'What do you do?'), explain that you help users find the best products from our inventory using AI search.

2. SEARCH & CONTEXT (RAG):
   - You will be provided with a 'Context' containing product details from our database.
   - ONLY recommend products that are present in the provided Context.
   - IF the user asks for a specific category (e.g., 'Shoes') and the Context contains irrelevant items (e.g., 'Laptops'), IGNORE the irrelevant items.
   - IF the Context is empty or none of the products match the user's request, strictly say: 'I'm sorry, we currently don't have [product] in our store. Can I help you find something else?'

3. NO HALLUCINATION:
   - Never invent products, prices, or features that are not in the Context.
   - If you are unsure, admit it.

4. RESPONSE STYLE:
   - Keep answers short and scannable.
   - Use Bullet points for product features.
   - Always mention the Price if available."""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Query: {query}\n\nContext: {context}"}
                ],
                "max_tokens": 500
            },
            timeout=60.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Groq API failed")
        return response.json()["choices"][0]["message"]["content"]

# General query handler
async def handle_general_query(query: str) -> str:
    system_prompt = """You are 'NeuSearch AI', a professional Shopping Assistant. Handle general queries warmly:
- For greetings: Welcome them and ask how you can help find products
- For questions about you: Explain you help find products using AI search
- Keep responses short and friendly"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 150
            },
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return "Hello! I'm NeuSearch AI. How can I help you find products today?"

# Admin Endpoints
@app.post("/admin/add-product", response_model=ProductResponse)
async def add_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@app.post("/admin/ingest-all", response_model=IngestResponse)
async def ingest_all_products(db: AsyncSession = Depends(get_db)):
    try:
        # Get all products
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        
        # Clear existing embeddings
        await db.execute(text("DELETE FROM product_embeddings"))
        await db.commit()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " "]
        )
        
        total_embeddings = 0
        
        for product in products:
            # Create content for embedding
            content = f"Product: {product.name}\nCategory: {product.category}\nPrice: ${product.price}\nDescription: {product.description}"
            
            # Split content into chunks
            chunks = text_splitter.split_text(content)
            
            for chunk in chunks:
                # Generate embedding
                embedding = await get_embedding(chunk)
                
                # Save to database
                db_embedding = ProductEmbedding(
                    product_id=product.id,
                    content_chunk=chunk,
                    embedding=embedding
                )
                db.add(db_embedding)
                total_embeddings += 1
        
        await db.commit()
        
        return IngestResponse(
            message="Successfully ingested all products",
            processed_products=len(products),
            total_embeddings=total_embeddings
        )
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        query_lower = request.query.lower().strip()
        
        # Simple pattern matching fallback for greetings - exact matches only
        greeting_patterns = ['hi', 'hello', 'hey']
        general_patterns = ['who are you', 'what are you', 'what do you do']
        
        # Direct pattern matching for common greetings - exact word matches
        if query_lower in greeting_patterns or any(pattern == query_lower for pattern in general_patterns):
            return ChatResponse(
                response="Hello! I'm NeuSearch AI, your shopping assistant. I help you find the best products using AI search. What are you looking for today?",
                products=[]
            )
        
        # Try intent classification with Groq
        try:
            intent = await classify_intent(request.query)
            print(f"Intent classified as: {intent}")  # Debug log
            
            # Handle GENERAL_QUERY without database search
            if "GENERAL" in intent.upper():
                general_response = await handle_general_query(request.query)
                return ChatResponse(
                    response=general_response,
                    products=[]
                )
        except Exception as e:
            print(f"Intent classification failed: {e}")  # Debug log
            # Continue to product search if intent fails
        
        # Handle PRODUCT_QUERY with database search
        # Check if products exist
        product_count = await db.execute(text("SELECT COUNT(*) FROM products"))
        if product_count.scalar() == 0:
            return ChatResponse(
                response="I'm sorry, we don't have any products in our store right now.",
                products=[]
            )
        
        # Check for 'list all' queries - skip category filtering
        list_all_patterns = ['list all', 'show all', 'all products', 'what do you have']
        is_list_all = any(pattern in query_lower for pattern in list_all_patterns)
        
        if is_list_all:
            result = await db.execute(select(Product))
            all_products = result.scalars().all()
            products_list = [ProductResponse(
                id=p.id, name=p.name, price=p.price, 
                description=p.description, category=p.category
            ) for p in all_products]
            
            return ChatResponse(
                response=f"Here are all our products ({len(all_products)} total):",
                products=products_list[:10]
            )
        
        # Generate query embedding
        query_embedding = await get_embedding(request.query)
        
        # SQL Change: Use relaxed threshold of 0.5 and return top 10 results
        search_query = text("""
            SELECT p.*, pe.embedding <=> :query_embedding as distance
            FROM products p
            JOIN product_embeddings pe ON p.id = pe.product_id
            WHERE (pe.embedding <=> :query_embedding) < 0.5
            ORDER BY distance
            LIMIT 10
        """)
        
        result = await db.execute(search_query, {"query_embedding": str(query_embedding)})
        search_results = result.fetchall()
        
        # Keyword Extraction: Extract main search term from user's query
        def extract_keyword(query: str) -> str:
            query = query.lower()
            keywords = ["shoe", "sneaker", "footwear", "laptop", "playstation", "coffee"]
            for keyword in keywords:
                if keyword in query:
                    return keyword
            return ""
        
        # The Validation Guard: Filter results based on keyword presence
        def filter_results(query, results):
            keyword = extract_keyword(query)
            if not keyword:
                return results  # Fallback to normal if no specific keyword found
            
            filtered_list = []
            for row in results:
                product = {
                    'name': row[1],
                    'description': row[3],
                    'category': row[4]
                }
                name_desc = (product['name'] + " " + product['description']).lower()
                
                # Validation: Product must mention the keyword
                if keyword in name_desc:
                    # Rank Adjustment: If keyword in name, move to top
                    if keyword in product['name'].lower():
                        filtered_list.insert(0, row)  # Move to top
                    else:
                        filtered_list.append(row)
            
            return filtered_list
        
        # Apply keyword validation
        filtered_results = filter_results(request.query, search_results)
        
        # Clean Response: If no product passes keyword check, return empty list
        if len(filtered_results) == 0:
            return ChatResponse(
                response="I'm sorry, we currently don't have that product in our store. Can I help you find something else?",
                products=[]
            )
        
        print(f"Final filtered results count: {len(filtered_results)}")
        
        # Build context and collect unique products from filtered results
        context_parts = []
        unique_products = {}
        
        for row in filtered_results:
            product_id = row[0]
            if product_id not in unique_products:
                unique_products[product_id] = ProductResponse(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    description=row[3],
                    category=row[4]
                )
            
            context_parts.append(f"- {row[1]} (${row[2]}) - {row[3]}")
        
        context = "\n".join(context_parts)
        
        # Generate AI response with context
        try:
            ai_response = await generate_chat_response(request.query, context)
        except:
            ai_response = "Here are the products I found for you."
        
        return ChatResponse(
            response=ai_response,
            products=list(unique_products.values())
        )
        
    except Exception as e:
        return ChatResponse(
            response="I'm sorry, I encountered an error. Please try again.",
            products=[]
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server running without database"}

@app.get("/")
async def root():
    # Serve React app in production
    static_path = os.path.join(os.getcwd(), "static")
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Shopping Expert API", "docs": "/docs"}

# Catch-all route for React Router (must be last)
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Don't interfere with API routes or static files
    if full_path.startswith(("admin/", "chat", "health", "docs", "openapi.json", "static/")):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve React app for all other routes
    static_path = os.path.join(os.getcwd(), "static")
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)