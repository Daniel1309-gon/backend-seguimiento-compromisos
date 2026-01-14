from fastapi import FastAPI, HTTPException, Depends, Security
from sqlalchemy.orm import Session
from sqlalchemy import case, func, extract, text
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi_azure_auth.user import User

import models.models as models
import database
from config import settings
from auth import azure_scheme
from contextlib import asynccontextmanager
from routes import auditorias, auditors, compromisos, stats, admin, mejoras


@asynccontextmanager
async def lifespan(app: FastAPI):
    await azure_scheme.openid_config.load_config()
    yield


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

