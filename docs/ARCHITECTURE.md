# Placement Intelligence Platform — Architecture

## High-Level Architecture

```
+-------------------+         +-------------------+         +-------------------+
|    FRONTEND       |  HTTP   |     BACKEND       |   SQL   |    DATABASE       |
|  Next.js (Vercel) | ------> |  FastAPI (Render)  | ------> | Supabase Postgres |
|  TypeScript       |         |  Python            |         | + pgvector        |
|  Tailwind+Shadcn  |         |  Async             |         |                   |
+-------------------+         +--------+-----------+         +-------------------+
                                       |
                              +--------v-----------+
                              |    AI SERVICES      |
                              |  Gemini API         |
                              |  Whisper (STT)      |
                              |  Piper (TTS)        |
                              +---------------------+
```

## Backend Pattern
Clean Architecture with Domain-Driven Design:
- **API Layer** (Routes/Controllers) → `app/api/routes/`
- **Service Layer** (Business Logic) → `app/services/`
- **AI Services** (Modular, replaceable) → `app/services/ai/`
- **Repository Layer** (SQLAlchemy ORM) → `app/models/`
- **Async Tasks** (Celery) → `app/tasks/`

## AI Services
All AI services extend `BaseAIService` or its sub-interfaces:
- `BaseQuestionGenerator` → InterviewGenerator, FollowUpGenerator
- `BaseEvaluator` → Evaluator
- `BaseParser` → ResumeParser, KnowledgeExtractor
- `BaseRecommender` → RecommendationEngine
- `BaseAIService` → VoiceEngine, GeminiClient

## Frontend Architecture
- **State**: Zustand (auth + interview session) + TanStack Query (server data)
- **Forms**: React Hook Form + Zod validation
- **Components**: Shadcn UI base + extracted domain components
- **Hooks**: Custom hooks wrapping TanStack Query for each domain

## Async Processing (Celery)
- Experience metadata extraction
- Question embedding generation
- Weakness detection post-evaluation
- Recommendation regeneration
- Company analytics recomputation (with 90-day time weighting)
