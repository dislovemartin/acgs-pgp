from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "ACGS-PGP Synthesis Service"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    DEBUG: bool = True
    
    # Database settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "synthesis_test")
    SQLALCHEMY_DATABASE_URL: str = os.getenv(
        "SQLALCHEMY_DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "False").lower() == "true"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
    ]
    
    # LLM settings
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092,localhost:9093")
    KAFKA_POLICY_UPDATES_TOPIC: str = os.getenv("KAFKA_POLICY_UPDATES_TOPIC", "policy-updates")
    
    # Policy Service API
    POLICY_SERVICE_URL: str = os.getenv("POLICY_SERVICE_URL", "http://policy-service:8000")
    
    class Config:
        case_sensitive = True

settings = Settings()
