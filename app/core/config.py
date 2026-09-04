from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IoT Device API"
    environment: str = "local"
    debug: bool = True

    database_url: str = "sqlite:///./iot.db"

    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="IOT_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
