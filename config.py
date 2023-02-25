import os
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseSettings
import logging
from loguru import logger
from types import FrameType
from typing import cast, List, Tuple, Dict, Any
import sys
from functools import lru_cache


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod

    class Config:
        env_file = ".env"


class Config(BaseAppSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FastAPI example application"
    version: str = "0.0.0"

    max_connection_count: int = 10
    min_connection_count: int = 10

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    LOG_FILE_PATH = "logs/"
    LOG_FILE_NAME = "LAIZHOU.log"
    LOG_LEVEL = "INFO"
    LOG_FILE_SIZE = "10 MB"
    LOG_FILE_SUM = 10

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str
    REDIS_DATABASE: str

    POOLS_NUMS = 2
    SCHEDULER_TIMEZONE: str

    TABLE_MAIN = os.getenv("TABLE_MAIN")
    KEY_MAIN = os.getenv("KEY_MAIN")
    TABLE_H2_LEAKAGE_DATA = os.getenv("TABLE_H2_LEAKAGE_DATA")
    KEY_H2_LEAKAGE_DATA = os.getenv("KEY_H2_LEAKAGE_DATA")
    TABLE_H2_LEAKAGE_DATA_BEGIN = os.getenv("TABLE_H2_LEAKAGE_DATA_BEGIN")
    KEY_H2_LEAKAGE_DATA_BEGIN = os.getenv("KEY_H2_LEAKAGE_DATA_BEGIN")
    
    WSGI_HOST = os.getenv("WEB_SERVER_GATEWAY_INTERFACE_HOST")
    WSGI_PORT = int(os.getenv("WEB_SERVER_GATEWAY_INTERFACE_PORT"))
    RELOAD = eval(os.getenv("RELOAD"))

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
    
    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]

        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])


# environments: Dict[AppEnvTypes, Type[AppSettings]] = {
#     AppEnvTypes.dev: DevAppSettings,
#     AppEnvTypes.prod: ProdAppSettings,
#     AppEnvTypes.test: TestAppSettings,
# }


@lru_cache()
def get_app_settings() -> Config:
    app_env = BaseAppSettings().app_env
    # config = environments[app_env]
    config = Config
    return config()