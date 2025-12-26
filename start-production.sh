#!/bin/bash

echo "🚀 Starting AI Shopping Expert in Production Mode"

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ .env.production file not found!"
    echo "Please copy .env.production template and add your API keys"
    exit 1
fi

# Load environment variables
export $(cat .env.production | xargs)

# Start services
echo "📦 Starting PostgreSQL and Application..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Application is running!"
echo "🌐 Frontend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "❤️  Health Check: http://localhost:8000/health"

echo ""
echo "📋 Next Steps:"
echo "1. Add products: POST /admin/add-product"
echo "2. Generate embeddings: POST /admin/ingest-all"
echo "3. Test chat: POST /chat"