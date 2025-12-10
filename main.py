from fastapi import FastAPI, HTTPException, Depends, Security
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi_azure_auth.user import User

import models.models as models
import schemas.schemas as schemas
import database
from config import settings
from auth import azure_scheme
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await azure_scheme.openid_config.load_config()
    yield

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='Seguimiento de compromisos de las Auditorías',
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.ID_APLICACION_CLIENTE,
        "scopes": settings.FULL_SCOPE_URI,
    }
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/auditors/', response_model=schemas.Auditor)
def create_auditor(auditor: schemas.AuditorCreate, db: Session = Depends(get_db)):
    db_auditor = models.Auditor(**auditor.dict())
    db.add(db_auditor)
    db.commit()
    db.refresh(db_auditor)
    return db_auditor

@app.get('/auditors/', response_model=List[schemas.Auditor])
def read_auditors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    auditors = db.query(models.Auditor).offset(skip).limit(limit).all()
    return auditors

@app.post('/auditorias/', response_model=schemas.Auditoria)
def create_auditoria(auditoria: schemas.AuditoriaCreate, 
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme)):

    email_usuario = user.get_claim("preferred_username")
    nombre_usuario = user.get_claim("name")

    print(f'Usuario autenticado: {nombre_usuario} ({email_usuario})')

    db_auditor = db.query(models.Auditor).filter(models.Auditor.aud_user == auditoria.user_aud).first()
    if not db_auditor:
        raise HTTPException(status_code=400, detail="Auditor no existe")
    db_auditoria = models.Auditoria(**auditoria.dict())
    db.add(db_auditoria)
    db.commit()
    db.refresh(db_auditoria)
    return db_auditoria

@app.get('/auditorias/', response_model=List[schemas.Auditoria])
def get_auditorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    auditorias = db.query(models.Auditoria).offset(skip).limit(limit).all()
    return auditorias

@app.post('/mejoras/', response_model=schemas.OpMejora)
def create_mejora(op_mejora: schemas.OpMejoraCreate, aud_id: int, db: Session = Depends(get_db)):
    db_auditoria = db.query(models.Auditoria).filter(models.Auditoria.id_aud == aud_id).first()
    if not db_auditoria:
        raise HTTPException(status_code=400, detail="Auditoría no existe")
    db_mejora = models.OpMejora(**op_mejora.dict(), aud_id=aud_id)
    db.add(db_mejora)
    db.commit()
    db.refresh(db_mejora)
    return db_mejora

@app.get('/mejoras/', response_model=List[schemas.OpMejora])
def read_mejoras(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    mejoras = db.query(models.OpMejora).offset(skip).limit(limit).all()
    return mejoras

@app.post('/compromisos/', response_model=schemas.Compromiso)
def create_compromiso(compromiso: schemas.CompromisoCreate, op_id: int, db: Session = Depends(get_db)):
    db_mejora = db.query(models.OpMejora).filter(models.OpMejora.id_op == op_id).first()
    if not db_mejora:
        raise HTTPException(status_code=400, detail="Oportunidad de mejora no existe")

    datos_compromiso = compromiso.dict()
    if datos_compromiso.get('deadline') is None:
        del datos_compromiso['deadline']

    db_compromiso = models.Compromiso(**datos_compromiso, op_id=op_id)
    db.add(db_compromiso)
    db.commit()
    db.refresh(db_compromiso)
    return db_compromiso

@app.get('/compromisos/', response_model=List[schemas.Compromiso])
def read_compromisos(skip: int = 0, limit: int = 10,    db: Session = Depends(get_db)):
    compromisos = db.query(models.Compromiso).offset(skip).limit(limit).all()
    return compromisos

@app.get('/auditorias/{auditoria_id}', response_model=schemas.Auditoria)
def read_auditoria(auditoria_id: int, db: Session = Depends(get_db)):
    db_auditoria = db.query(models.Auditoria).filter(models.Auditoria.id_aud == auditoria_id).first()
    if db_auditoria is None:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    return db_auditoria