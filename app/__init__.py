from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.core.config import get_app_settings
import warnings
warnings.filterwarnings("ignore")


settings = get_app_settings()

def create_app() -> FastAPI:
    settings.configure_logging()
    app = FastAPI(**settings.fastapi_kwargs)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_event_handler(
    #     "startup",
    #     create_start_app_handler(app, settings),
    # )
    # app.add_event_handler(
    #     "shutdown",
    #     create_stop_app_handler(app),
    # )

    # app.add_exception_handler(HTTPException, http_error_handler)
    # app.add_exception_handler(RequestValidationError, http422_error_handler)
    
    from app.myScheduler import scheduler
    if scheduler.state != 1: # 是否已运行
        scheduler.start()
        logger.info("Scheduler Start")

    from app.main import router as main_router
    app.include_router(main_router)

    return app