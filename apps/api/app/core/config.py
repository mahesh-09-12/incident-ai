from functools import lru_cache

from pydantic import model_validator
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
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""

    # =========================
    # AI
    # =========================
    OPENAI_API_KEY: str = ""
    OLLAMA_TIMEOUT_SECONDS: int = 240
    AI_PROVIDER: str = "gemini"  # "ollama" or "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    
    # Feature Flags
    MULTI_AGENT_ENABLED: bool = False

    # =========================
    # Storage
    # =========================
    STORAGE_PROVIDER: str = "cloudinary"  # "local" or "cloudinary"
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    @model_validator(mode="after")
    def validate_cloudinary_config(self) -> "Settings":
        if self.STORAGE_PROVIDER == "cloudinary":
            if not self.CLOUDINARY_CLOUD_NAME or not self.CLOUDINARY_API_KEY or not self.CLOUDINARY_API_SECRET:
                raise ValueError("Cloudinary configuration is missing. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET.")
        return self

    @property
    def is_cloudinary_enabled(self) -> bool:
        return self.STORAGE_PROVIDER == "cloudinary"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()