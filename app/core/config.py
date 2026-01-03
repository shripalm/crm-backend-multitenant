import json
import os
from pathlib import Path
from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve project root once at module import time. Keep it outside the
# Settings class so Pydantic doesn't treat it as an un-annotated model field.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # Application Settings (all from .env)
    PROJECT_NAME: str
    APP_ENV: str
    APP_HOST: str
    APP_PORT: int
    STAGE_PATH: str

    # Database Settings (all from .env)
    DB_URLS: dict[str, AnyUrl] = {}
    DB_KEYS: list[str] = []

    @field_validator("DB_URLS", mode="before")
    def parse_db_urls(cls, v: any):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("DB_URLS must be valid JSON")
        return v
    
    # get list of DB_KEYS from the keys of DB_URLS
    @field_validator("DB_KEYS", mode="after")
    def extract_db_keys(cls, v: list[str], info):
        db_urls = info.data.get("DB_URLS", {})
        return list(db_urls.keys())

    # Database Connection Pool Settings (all from .env)
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_POOL_TIMEOUT: int
    DB_POOL_RECYCLE: int

    # Security Settings (all from .env)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Logging Settings (from .env)
    LOG_LVL: str

    # Email Settings (Gmail SMTP) - UNUTILISED
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "rbrickkstechnologyemployees@gmail.com"
    SMTP_PASSWORD: str = "ggxk bzcx kise oaes"
    SMTP_FROM_EMAIL: str = "rbrickkstechnologyemployees@gmail.com"
    SMTP_FROM_NAME: str = "CRM System"

    # Email Settings (SendGrid) - ACTIVE
    SENDGRID_API_KEY: str = "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"
    SENDGRID_FROM_EMAIL: str = "rbrickkstechpvtltd@gmail.com"
    SENDGRID_FROM_NAME: str = "CRM System"

    # OTP Settings
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 4
      
    PAYTM_MERCHANT_ID: str
    PAYTM_MERCHANT_KEY: str
    PAYTM_WEBSITE: str = "WEBSTAGING"
    PAYTM_INDUSTRY_TYPE: str = "Retail"
    PAYTM_CHANNEL_ID: str = "WEB"
    PAYTM_STAGING: bool = True
    BASE_URL: str = "http://localhost:8000"  # Used for callback URLs
      
    # pydantic v2 style configuration
    # Use the module-level PROJECT_ROOT so Pydantic doesn't treat this as
    # a model field (avoids non-annotated attribute errors).
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra='ignore'
    )



settings = Settings()