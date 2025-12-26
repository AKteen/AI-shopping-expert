import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def clear_all_products():
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Remove the postgresql+asyncpg:// prefix for asyncpg
    db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(db_url)
    
    try:
        # Clear all products and embeddings
        await conn.execute("DELETE FROM product_embeddings")
        await conn.execute("DELETE FROM products")
        print("All products and embeddings cleared!")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(clear_all_products())