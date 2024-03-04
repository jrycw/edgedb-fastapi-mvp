from pydantic_settings import BaseSettings, SettingsConfigDict

# from typing import Annotated
# from pydantic import AfterValidator, HttpUrl
# HttpUrlString = Annotated[HttpUrl, AfterValidator(str)]
from .logging import CLogLevel


class Settings(BaseSettings):
    frontend_schema: str = "http"
    frontend_host: str = "localhost"
    frontend_port: int = 7000
    frontend_reload: bool = False
    frontend_log_json_format: bool = False
    frontend_log_level: CLogLevel = CLogLevel.INFO

    backend_schema: str = "http"
    backend_host: str = "localhost"
    backend_port: int = 8000
    backend_reload: bool = False
    backend_prefill: bool = False
    backend_log_json_format: bool = False
    backend_log_level: CLogLevel = CLogLevel.INFO

    tz: str = "UTC"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
