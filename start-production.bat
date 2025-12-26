@echo off
echo 🚀 Starting AI Shopping Expert in Production Mode

REM Check if .env.production exists
if not exist .env.production (
    echo ❌ .env.production file not found!
    echo Please copy .env.production template and add your API keys
    pause
    exit /b 1
)

echo 📦 Starting PostgreSQL and Application...
docker-compose up -d

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo ✅ Application is running!
echo 🌐 Frontend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo ❤️  Health Check: http://localhost:8000/health
echo.
echo 📋 Next Steps:
echo 1. Add products: POST /admin/add-product
echo 2. Generate embeddings: POST /admin/ingest-all
echo 3. Test chat: POST /chat

pause