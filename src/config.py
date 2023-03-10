from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Habitap API"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"
