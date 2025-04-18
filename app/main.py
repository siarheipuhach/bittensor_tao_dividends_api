import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from app.api.v1.routes import router as api_router
from app.auth.auth import verify_token
from app.cache.redis import redis_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_cache.connect()
    yield


app = FastAPI(title="Bittensor Tao Dividends API", lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1", dependencies=[Depends(verify_token)])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 Unhandled Exception:", exc)
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})
