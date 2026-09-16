from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # Application
    # =========================
    APP_NAME: str = "Incident AI API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"

    # =========================
    # Database
    # =========================
    DATABASE_URL: str

    # =========================
    # Security
    # =========================
    SECRET_KEY: str

    # =========================
    # AI
    # =========================
    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()