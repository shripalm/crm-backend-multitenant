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

    @field_validator("DB_URLS", mode="before")
    def parse_db_urls(cls, v: any):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("DB_URLS must be valid JSON")
        return v

    # Database Connection Pool Settings (all from .env)
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_POOL_TIMEOUT: int
    DB_POOL_RECYCLE: int

    # Security Settings (all from .env)
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Logging Settings (from .env)
    LOG_LVL: str

    # Client mappings and unit short (loaded from app-config.json)
    BRAND_CREATION: dict = {}
    UNIT_SHORT: dict = {}
    DAYS_SHORTS: dict = {}
    METRIC_FORMATS_CONFIG: dict = {}

    def load_app_config(self, config_path: str):
        import json
        import os
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, "r") as f:
            config = json.load(f)
            if not config:
                raise ValueError(f"App config file is empty: {config_path}")
            # brand-creation is a dict of tenant -> db_name
            db_mapping = config.get("brand-creation", {})
            # convert tenant keys to client keys (strip 'tenant_' prefix)
            self.BRAND_CREATION = db_mapping
            self.UNIT_SHORT = config.get("unit-short", {})
            self.DAYS_SHORTS = config.get("days-shorts", {})
            self.METRIC_FORMATS_CONFIG = config.get("metric-formats", {})


       
    # pydantic v2 style configuration
    # Use the module-level PROJECT_ROOT so Pydantic doesn't treat this as
    # a model field (avoids non-annotated attribute errors).
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra='ignore'
    )



settings = Settings()