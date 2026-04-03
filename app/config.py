from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_NAME: str
    ADMIN_IDS: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.DB_NAME}"

    @property
    def admin_list(self) -> List[int]:
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip().isdigit()]

settings = Settings()