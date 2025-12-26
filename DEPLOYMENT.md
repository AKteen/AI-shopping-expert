# 🚀 Production Deployment Guide

## Quick Start

1. **Setup Environment**:
   ```bash
   cp .env.production .env.production.local
   # Edit .env.production.local with your API keys
   ```

2. **Start Production**:
   ```bash
   # Linux/Mac
   chmod +x start-production.sh
   ./start-production.sh
   
   # Windows
   start-production.bat
   ```

3. **Access Application**:
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Manual Deployment

### Using Docker Compose
```bash
docker-compose up -d
```

### Using Docker Build
```bash
docker build -t ai-shopping-expert .
docker run -p 8000:8000 ai-shopping-expert
```

## Environment Variables

Required for production:
- `GROQ_API_KEY`: Your Groq API key
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_PASSWORD`: Database password

## Cloud Deployment

### AWS/GCP/Azure
1. Build and push Docker image
2. Deploy with managed PostgreSQL
3. Set environment variables
4. Configure load balancer

### Heroku
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set GROQ_API_KEY=your_key
git push heroku main
```

## Production Checklist

- ✅ Environment variables configured
- ✅ Database with pgvector extension
- ✅ CORS configured for your domain
- ✅ Static files served correctly
- ✅ Health checks working
- ✅ Error handling in place