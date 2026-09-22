"""Application settings from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Set up environment variables.

    Includes both database and CORS settings.
    """
    # Will pull from Azure App Service environment variables in deployment.
    model_config = SettingsConfigDict(env_file=".env")

    db_server: str
    db_name: str
    db_user: str
    db_password: str
    frontend_origin: str