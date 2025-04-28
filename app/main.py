import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from app.api.v1.routes import router as api_router
from app.auth.auth import verify_token
from app.cache.redis import redis_cache

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown."""
    await redis_cache.connect()
    yield


app = FastAPI(
    title="Bittensor Tao Dividends API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    api_router,
    prefix="/api/v1",
    dependencies=[Depends(verify_token)],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
