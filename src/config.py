from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Habitap API"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    database_url: str = Field(..., env='database_url')

    class Config:
        env_file = ".env"
