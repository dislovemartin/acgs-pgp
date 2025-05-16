from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "ACGS-PGP Runtime Governance Engine (RGE)"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Policy Service Configuration
    POLICY_SERVICE_URL: str = "http://policy-service:8000/api/v1"
    POLICY_UPDATE_INTERVAL: int = 60  # seconds
    
    # Kafka Configuration (for receiving policy updates)
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_POLICY_UPDATES_TOPIC: str = "policy-updates"
    KAFKA_GROUP_ID: str = "rge-service"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
