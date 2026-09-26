from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения. Читаются из .env."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/wallets"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
