from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # ClickHouse
    CLICKHOUSE_HOST: str = "clickhouse"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "airflow"
    CLICKHOUSE_PASSWORD: str = "airflow123"
    CLICKHOUSE_DB: str = "reports_db"
    
    # Keycloak
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "reports-realm"
    KEYCLOAK_CLIENT_ID: str = "reports-api"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()