from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./wanikani_mcp.db"
    wanikani_api_base_url: str = "https://api.wanikani.com/v2"
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8000
    debug: bool = False


settings = Settings()
