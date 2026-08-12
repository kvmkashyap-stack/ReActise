import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Central configuration for the application.
    Loads all environment variables from the .env file.
    """

    APP_NAME: str = "ReAct Agent"
    APP_VERSION: str = "1.0.0"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    SECRET_KEY: str = "fallback_secret_key_value_reactise"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    UPLOAD_FOLDER: str = "/tmp/uploads" if os.path.exists("/tmp") else "./uploads"
    WORKSPACES_FOLDER: str = "/tmp/workspaces" if os.path.exists("/tmp") else "./workspaces"

    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )
settings = Settings()
