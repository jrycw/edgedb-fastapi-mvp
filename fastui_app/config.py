from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    frontendhost: HttpUrl = "http://localhost"
    frontendport: int = 7000
    frontenddebug: bool = False

    backendhost: HttpUrl = "http://localhost"
    backendport: int = 8000

    tz: str = "UTC"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
# print(f"{settings=} from frontend")
