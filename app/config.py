from pydantic_settings import BaseSettings, SettingsConfigDict

# from typing import Annotated
# from pydantic import AfterValidator, HttpUrl
# HttpUrlString = Annotated[HttpUrl, AfterValidator(str)]


class Settings(BaseSettings):
    frontendschema: str = "http"
    frontendhost: str = "localhost"
    frontendport: int = 7000
    frontendreload: bool = False

    backendschema: str = "http"
    backendhost: str = "localhost"
    backendport: int = 8000
    backendreload: bool = False
    backendprefill: bool = False

    tz: str = "UTC"
    secret_csrf: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
