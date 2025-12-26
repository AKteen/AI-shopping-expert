from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

# SQLAlchemy Models
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    
    embeddings = relationship("ProductEmbedding", back_populates="product", cascade="all, delete-orphan")

class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    content_chunk = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    
    product = relationship("Product", back_populates="embeddings")
    
    __table_args__ = (
        Index("idx_embedding_vector", "embedding", postgresql_using="ivfflat"),
    )

