from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Code Review Agent"
    DEBUG: bool = False
    DEFAULT_LOCALE: str = "en"
    SUPPORTED_LOCALES: list[str] = ["en", "ne"]

    # Encryption
    ENCRYPTION_KEY: str = Field(..., description="Encryption key")
    ENCRYPTION_SALT: str = Field(..., description="Encryption salt")

    # MongoDB
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_USER: str = ""
    MONGO_PASSWORD: str = ""
    MONGO_DB: str = "ai_db"

    @property
    def MONGO_URL(self) -> str:
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return (
                f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}"
                f"@{self.MONGO_HOST}:{self.MONGO_PORT}"
            )
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"

    # Valkey (Redis-compatible)
    VALKEY_HOST: str = "localhost"
    VALKEY_PORT: int = 6379
    VALKEY_DB: int = 0
    VALKEY_PASSWORD: str | None = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
