from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models.models as models
import database
from config import settings
from auth import azure_scheme
from contextlib import asynccontextmanager
from routes import auditorias, auditors, compromisos, stats, admin, mejoras, follow_up

import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from fastapi_limiter import FastAPILimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await azure_scheme.openid_config.load_config()

    redis_connection = redis.from_url(settings.REDIS_URL, 
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
    encoding="utf8", 
    decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis_connection), prefix="fastapi-cache")

    await FastAPILimiter.init(redis_connection)

    print("Conectado a Redis para rate limiting y caching")

    yield

    await redis_connection.close()
    print("Desconectado de Redis")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Seguimiento de compromisos de las Auditorías",
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.ID_APLICACION_CLIENTE,
        "scopes": settings.FULL_SCOPE_URI,
    },
    version="1.0.0",
)

origins = [
    "http://localhost:3000",
    "http://192.168.56.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(auditors.router)
app.include_router(auditorias.router)
app.include_router(mejoras.router)
app.include_router(compromisos.router)
app.include_router(stats.router)
app.include_router(follow_up.router)

