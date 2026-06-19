# Placement Intelligence Platform

A continuously learning placement preparation ecosystem. Not just an AI mock interviewer — it collects real interview experiences, builds company-specific intelligence, conducts adaptive AI-powered mock interviews, and provides personalized placement readiness analytics.

## Architecture

```
Frontend (Next.js + TypeScript)  →  Backend (FastAPI + Python)  →  Database (Supabase PostgreSQL + pgvector)
                                          ↓
                                    AI Services (Gemini API)
                                    Voice (Whisper + Piper)
                                    Async Tasks (Celery + Redis)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, Shadcn UI, Zustand, TanStack Query |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic, Pydantic |
| Database | PostgreSQL (Supabase) + pgvector |
| AI | Google Gemini 2.0 Flash, Whisper (STT), Piper (TTS) |
| Auth | Supabase Auth (Email + Google OAuth), JWT |
| Deployment | Vercel (frontend), Render (backend), Supabase (database) |

## Quick Start

### Backend
```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in values
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # Fill in values
npm run dev
```

### Docker (Database + Redis)
```bash
docker-compose up -d
```

## API Documentation

Once the backend is running: http://localhost:8000/api/docs

## Features

- **Authentication** — Email/password + Google OAuth
- **Student Dashboard** — Stats, trends, performance overview
- **Interview Experience Collection** — Community-driven knowledge base
- **Company Intelligence** — AI-extracted insights per company
- **Resume Intelligence** — AI parsing, skill extraction, gap analysis
- **AI Mock Interviews** — Resume-aware, company-specific, adaptive
- **Voice Interviews** — Speech-to-text + text-to-speech pipeline
- **Evaluation Engine** — Explainable 6-dimension scoring
- **Interview Replay** — Review past interviews with ideal answers
- **Weakness Detection** — Track recurring weaknesses across interviews
- **Learning Recommendations** — Personalized study plans
- **Placement Readiness** — Per-company readiness scores
- **Knowledge Base Search** — Hybrid text + semantic search
- **Admin Panel** — Company management, experience moderation, analytics

## Testing

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

## Project Structure

```
placement-intelligence-platform/
├── backend/          # FastAPI backend (42 API endpoints)
│   ├── app/
│   │   ├── api/routes/     # 14 route modules
│   │   ├── core/           # Config, security
│   │   ├── db/             # Database session
│   │   ├── middleware/     # Rate limiting, activity logging
│   │   ├── models/         # 17 SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic + AI services
│   │   └── utils/          # Helpers, constants
│   ├── alembic/            # Database migrations
│   └── tests/              # 22 unit tests
├── frontend/         # Next.js frontend (24 pages)
│   └── src/
│       ├── app/            # Pages (auth, dashboard, admin)
│       ├── components/     # UI components (Shadcn + custom)
│       ├── lib/            # API client, Supabase, utilities
│       ├── stores/         # Zustand state management
│       └── types/          # TypeScript interfaces
└── docker-compose.yml
```
