from pydantic_settings import BaseSettings, SettingsConfigDict

# from typing import Annotated
# from pydantic import AfterValidator, HttpUrl
# HttpUrlString = Annotated[HttpUrl, AfterValidator(str)]
from .logging import CLogLevel


# TODO: Decouple the messy and decide what variables should be include in the .env
class Settings(BaseSettings):
    frontend_schema: str = "http"
    frontend_host: str = "localhost"
    frontend_port: int = 7000
    frontend_reload: bool = False
    frontend_log_json_format: bool = False
    frontend_log_level: CLogLevel = CLogLevel.INFO
    tz: str = "UTC"

    backend_schema: str = "http"
    backend_host: str = "localhost"
    backend_port: int = 8000
    backend_reload: bool = False
    backend_prefill: bool = False
    backend_log_json_format: bool = False
    backend_log_level: CLogLevel = CLogLevel.INFO

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


def get_backend_http_client_baseurl():
    return (
        f"{settings.backend_schema}://{settings.backend_host}:{settings.backend_port}"
    )


def get_frontend_http_client_baseurl():
    return f"{settings.frontend_schema}://{settings.frontend_host}:{settings.frontend_port}"


# TODO: EdgeDB cloud
def get_db_dsn():
    pass
