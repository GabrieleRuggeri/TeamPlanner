"""Application configuration utilities."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for TeamPlanner.

    Attributes:
        app_name: Display name for the application.
        database_url: Database connection string.
        environment: Runtime environment label.
    """

    app_name: str = "TeamPlanner"
    database_url: str = "sqlite:///./teamplanner.db"
    environment: str = "local"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance.

    Returns:
        Cached Settings object.
    """

    return Settings()
