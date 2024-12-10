import logging

import sentry_sdk

from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import bot
from app.core.db import init_db
from app.core.config import settings
from app.api.main import api_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# Create a Sentry account later for monitoring and logging
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Initializing bot application")
    await bot.bot_app.initialize()

    logger.info(f"Setting webhook")
    logging.info(await bot.set_webhook())

    logger.info("Creating initial data")
    await init_db() 
    logger.info("Done")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    lifespan=lifespan,
    root_path="/api"
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    print(settings.all_cors_origins)
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=settings.all_cors_origins,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(api_router)
