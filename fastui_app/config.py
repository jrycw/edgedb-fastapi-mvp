from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    frontendhost: HttpUrl = "http://localhost"
    frontendport: int = 7000

    backendhost: HttpUrl = "http://localhost"
    backendport: int = 8000

    model_config = SettingsConfigDict(
        env_file="frontend.env", env_file_encoding="utf-8"
    )


settings = Settings()
print(f"{settings=} from frontend")
