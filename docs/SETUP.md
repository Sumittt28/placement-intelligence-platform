# Local Development Setup

## Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (for Postgres + Redis)

## 1. Clone & Start Infrastructure
```bash
git clone <repo-url>
cd placement-intelligence-platform
docker-compose up -d  # Starts Postgres + Redis
```

## 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in values
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local  # Fill in values
npm run dev
```

## 4. Start Celery Worker
```bash
cd backend
celery -A app.worker worker --loglevel=info
```

## Environment Variables
| Variable | Description | Where |
|----------|-------------|-------|
| DATABASE_URL | PostgreSQL connection string | Backend .env |
| SUPABASE_URL | Supabase project URL | Both |
| SUPABASE_KEY | Supabase anon key | Both |
| SUPABASE_SERVICE_KEY | Supabase service role key | Backend .env |
| GEMINI_API_KEY | Google Gemini API key | Backend .env |
| JWT_SECRET | JWT signing secret | Backend .env |
| REDIS_URL | Redis connection URL | Backend .env |
| NEXT_PUBLIC_API_URL | Backend API base URL | Frontend .env |

## Production Deployment
- **Frontend**: Vercel (auto-deploy from `main`)
- **Backend**: Render (Docker-based)
- **Database**: Supabase PostgreSQL + pgvector
