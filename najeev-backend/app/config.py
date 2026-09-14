from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str
    mongodb_url: str
    mongodb_database: str = 'notes'
    jwt_secret: str = Field(min_length=32)
    access_token_minutes: int = Field(default=30, ge=1, le=1440)
    admin_username: str = 'admin'
    admin_password: str = Field(min_length=12)


@lru_cache
def get_settings():
    return Settings()
