from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Placement Intelligence Platform"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/placement_intel"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # ── AI Provider ─────────────────────────────────────────────────────────────
    # Options: "groq" (recommended) | "gemini" (legacy) | "ollama" (local dev)
    AI_PROVIDER: str = "groq"

    # Groq (primary — free tier, fast inference)
    # Get your free key at: https://console.groq.com/keys
    GROQ_API_KEY: str = ""
    # Heavy tasks: evaluation, resume parsing, recommendations (1000 req/day free)
    GROQ_MODEL_SMART: str = "llama-3.3-70b-versatile"
    # Light tasks: question generation, follow-ups (14400 req/day free)
    GROQ_MODEL_FAST: str = "llama-3.1-8b-instant"

    # Gemini (legacy fallback — kept for backward compatibility)
    GEMINI_API_KEY: str = ""

    # Ollama (local dev — run `ollama pull qwen2.5:7b` first)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    # ────────────────────────────────────────────────────────────────────────────

    # Auth
    JWT_SECRET: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
