import logging
from typing import Any, Dict, List
from loguru import logger
from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings
import sys

class AppSettings(BaseAppSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "LaiZhou"
    version: str = "2.0"

    max_connection_count: int = 10
    min_connection_count: int = 10

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    # uvicorn.access 显示http请求
    loggers: List[str] = ["uvicorn.asgi"]

    LOG_FILE_PATH = "logs/"
    LOG_FILE_NAME = "LAIZHOU.log"
    LOG_LEVEL = "INFO"
    LOG_FILE_SIZE = "10 MB"
    LOG_FILE_SUM = 10

    # 环境变量 > .env > 当前设置
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str
    REDIS_DATABASE: str

    POOLS_NUMS: int = 2
    SCHEDULER_TIMEZONE: str

    TABLE_MAIN: str
    KEY_MAIN: str
    TABLE_H2_LEAKAGE_DATA: str
    KEY_H2_LEAKAGE_DATA: str
    TABLE_H2_LEAKAGE_DATA_BEGIN: str
    KEY_H2_LEAKAGE_DATA_BEGIN: str
    
    WSGI_HOST: str
    WSGI_PORT: int
    RELOAD: bool

    class Config:
        pass

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

        logger.configure(handlers=[
            {
                "sink": self.LOG_FILE_PATH + self.LOG_FILE_NAME, 
                "level": self.logging_level,
                "rotation": self.LOG_FILE_SIZE,
                "retention": self.LOG_FILE_SUM
            }
        ])
        logger.add(sys.stderr, level=self.logging_level)
