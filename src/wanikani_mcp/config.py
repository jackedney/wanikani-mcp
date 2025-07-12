from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database Configuration
    database_url: str = "sqlite:///./wanikani_mcp.db"

    # WaniKani API Configuration
    wanikani_api_base_url: str = "https://api.wanikani.com/v2"
    wanikani_rate_limit: int = 60  # requests per minute

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"

    # Background Sync Configuration
    sync_interval_minutes: int = 30
    max_concurrent_syncs: int = 3

    # Optional: Monitoring
    sentry_dsn: str = ""


settings = Settings()
