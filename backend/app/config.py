from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql+asyncpg://rateuser:ratepass@localhost:5432/ratelimiter"

    class Config:
        env_file = ".env"

settings = Settings()