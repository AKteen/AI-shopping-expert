# AI Shopping Expert - RAG-based Shopping Assistant

A modern AI-powered shopping assistant built with FastAPI, React, and PostgreSQL with pgvector for semantic search.

## Architecture Overview

- **Backend**: FastAPI with async SQLAlchemy, pgvector for embeddings
- **Frontend**: React with Vite and Tailwind CSS
- **AI**: Ollama with mxbai-embed-large for embeddings and Llama3 for chat
- **Database**: PostgreSQL with pgvector extension

## Prerequisites

1. **PostgreSQL with pgvector**:
   ```bash
   # Install PostgreSQL and pgvector extension
   # Create database: ai_shopping
   ```

2. **Ollama**:
   ```bash
   # Install Ollama and pull required models
   ollama pull mxbai-embed-large
   ollama pull llama3
   ```

## Backend Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Update `.env` with your database credentials
   - Ensure Ollama is running on localhost:11434

3. **Run the server**:
   ```bash
   python main.py
   # Server runs on http://localhost:8000
   ```

## Frontend Setup

1. **Install dependencies**:
   ```bash
   cd neu-app
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   # Frontend runs on http://localhost:3000
   ```

## API Endpoints

### Admin Endpoints
- `POST /admin/add-product`: Add a new product
- `POST /admin/ingest-all`: Generate embeddings for all products

### User Endpoints
- `POST /chat`: RAG-based product search and recommendations
- `GET /health`: Health check

## Usage Flow

1. **Add Products**: Use `/admin/add-product` to add products to the database
2. **Generate Embeddings**: Call `/admin/ingest-all` to create vector embeddings
3. **Chat Interface**: Use the React frontend to search for products naturally

## Example Product Data

```json
{
  "name": "Nike Air Max 270",
  "price": 150.00,
  "description": "Comfortable running shoes with Air Max technology, perfect for daily workouts and casual wear.",
  "category": "Footwear"
}
```

## Example Chat Queries

- "I need blue gym shoes"
- "Show me wireless headphones under $100"
- "What laptops do you recommend for students?"

## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLAlchemy models & Pydantic schemas
│   ├── database.py      # Database configuration
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment variables
└── neu-app/
    ├── src/
    │   ├── components/
    │   │   └── ChatWindow.jsx    # Main chat interface
    │   ├── hooks/
    │   │   └── useChat.js        # API management hook
    │   ├── App.jsx              # Main app component
    │   ├── main.jsx             # React entry point
    │   └── style.css            # Tailwind styles
    ├── package.json             # Node dependencies
    ├── vite.config.js          # Vite configuration
    └── tailwind.config.js      # Tailwind configuration
```

## Development Notes

- The backend uses async/await for all database and AI operations
- Vector similarity search uses pgvector's `<=>` operator
- Text chunking is handled by LangChain's RecursiveCharacterTextSplitter
- Frontend includes loading states and error handling
- Clean, modular architecture suitable for internship projects