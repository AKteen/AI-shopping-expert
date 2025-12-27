# 🛒 AI Shopping Expert

Live: https://inspiring-wisdom-production.up.railway.app/

A modern AI-powered shopping assistant built with **FastAPI**, **React**, and **PostgreSQL** featuring **RAG (Retrieval-Augmented Generation)** for intelligent product search and recommendations.



## ✨ Features

- 🤖 **AI-Powered Chat**: Natural language product search using Groq's Llama3
- 🔍 **RAG Search**: Vector similarity search with pgvector for accurate results
- 🛡️ **Keyword Validation**: Hybrid search with keyword filtering to prevent irrelevant results
- 📱 **Modern UI**: Clean React interface with Tailwind CSS
- 🚀 **Production Ready**: Dockerized deployment with Railway/Heroku support
- 🔒 **Secure**: Environment-based configuration with API key management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │────│  FastAPI Backend │────│ PostgreSQL + AI │
│   (Vite + Tailwind) │    │  (Async + RAG)   │    │ (pgvector + Groq)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python async framework)
- SQLAlchemy + asyncpg (Database ORM)
- pgvector (Vector similarity search)
- Groq API (Llama3 for chat responses)
- HuggingFace (Text embeddings)

**Frontend:**
- React 18 + Vite
- Tailwind CSS
- Custom hooks for API management

**Database:**
- PostgreSQL with pgvector extension
- Vector embeddings for semantic search

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL with pgvector
- Groq API key

### 1. Clone Repository
```bash
git clone https://github.com/AKteen/AI-shopping-expert.git
cd AI-shopping-expert
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python main.py
```

### 3. Frontend Setup
```bash
cd neu-app
npm install
npm run dev
```

### 4. Environment Variables
```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
HF_API_TOKEN=your_huggingface_token
CHAT_MODEL=llama3-8b-8192
```

## 🐳 Docker Deployment

### Local with Docker Compose
```bash
docker-compose up -d
```

### Railway Deployment
1. Connect GitHub repo to Railway
2. Add environment variables
3. Auto-deploys from main branch

## 📚 API Endpoints

### Admin Endpoints
- `POST /admin/add-product` - Add new products
- `POST /admin/ingest-all` - Generate embeddings

### User Endpoints
- `POST /chat` - AI chat with product search
- `GET /health` - Health check
- `GET /docs` - API documentation

## 💬 Usage Examples

### Add Products
```json
POST /admin/add-product
{
  "name": "Nike Air Max 270",
  "price": 150.00,
  "description": "Comfortable running shoes with Air Max technology",
  "category": "Footwear"
}
```

### Chat Queries
- "I need blue gym shoes"
- "Show me wireless headphones under $100"
- "What laptops do you recommend for students?"

## 🔧 Key Features Explained

### RAG (Retrieval-Augmented Generation)
1. **Vector Search**: Converts user queries to embeddings
2. **Similarity Matching**: Finds relevant products using cosine similarity
3. **Context Generation**: Provides product context to AI model
4. **Smart Responses**: AI generates natural responses with actual product data

### Keyword-Validated Hybrid Search
```python
# Prevents irrelevant results like "coffee machines" for "shoes"
def filter_results(query, results):
    keyword = extract_keyword(query)  # "shoe" from "i want shoes"
    return [product for product in results if keyword in product.name.lower()]
```

### Production Optimizations
- **Memory Efficient**: Uses HuggingFace Inference API instead of local models
- **Error Resilient**: Graceful fallbacks for API/DB failures
- **Railway Compatible**: Dynamic port handling and static file serving

## 📁 Project Structure

```
├── backend/                 # FastAPI application
│   ├── main.py             # Main application file
│   ├── models.py           # Database models
│   ├── database.py         # Database configuration
│   └── requirements.txt    # Python dependencies
├── neu-app/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── hooks/          # Custom hooks
│   └── package.json        # Node dependencies
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Local development
└── README.md              # This file
```

## 🌟 Live Demo

**Deployed on Railway:** https://inspiring-wisdom-production.up.railway.app/

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request


## 🙏 Acknowledgments

- [Groq](https://groq.com) for fast AI inference
- [HuggingFace](https://huggingface.co) for embedding models
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity search
- [Railway](https://railway.app) for seamless deployment

---

**Built with ❤️ for intelligent e-commerce experiences**
