import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        extra="ignore"
    )

    PROJECT_NAME: str = "दृष्टि (Drishti) — Urban Road Intelligence API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_DEBUG: bool = False
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8501",
        "https://dsjangid.github.io",
        "*"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./drishti_municipal.db"
    
    # AI Model Path
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/drishti_potholedetect_v1.pt")
    
    # IRC Cost Rate Card (INR per Metric Tonne of Hot-Mix Asphalt)
    IRC_ASPHALT_RATE_PER_MT: float = 3750.0  # ₹3,750 per MT
    BASE_MOBILIZATION_FEE: float = 3000.0   # ₹3,000 baseline crew dispatch

settings = Settings()

