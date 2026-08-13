from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  TOKEN: SecretStr
  postgres_db: str
  postgres_user: str
  postgres_password: SecretStr
  postgres_host: str
  postgres_port: int
  database_url: str
  model_config: SettingsConfigDict = SettingsConfigDict(
    env_file='.env',
    env_file_encoding='utf-8'
)
  
config = Settings()
