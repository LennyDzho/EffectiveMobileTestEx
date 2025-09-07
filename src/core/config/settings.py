from pathlib import Path
from typing import Optional

from environs import Env
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class DatabaseConfig(BaseModel):
    database: str
    user: str
    password: str
    host: str
    port: int

    def connection_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:"
            f"{self.port}/{self.database}"
        )


class Settings(BaseModel):
    db: DatabaseConfig


def load_settings() -> Settings:
    env_path = BASE_DIR / ".env"
    env = Env()

    env.read_env(env_path)

    return Settings(
        db=DatabaseConfig(
            database=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASSWORD"),
            host=env.str("DB_HOST"),
            port=env.int("DB_PORT"),
        ),
    )


settings: Settings = load_settings()