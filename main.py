from fastapi import FastAPI, HTTPException, Depends, Security
from sqlalchemy.orm import Session
from sqlalchemy import case, func, extract
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

app = FastAPI(
    title="Seguimiento de compromisos de las Auditorías",
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.ID_APLICACION_CLIENTE,
        "scopes": settings.FULL_SCOPE_URI,
    },
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


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/auditors/", response_model=schemas.Auditor)
def create_auditor(auditor: schemas.AuditorCreate, db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    db_auditor = models.Auditor(**auditor.dict())
    db.add(db_auditor)
    db.commit()
    db.refresh(db_auditor)
    return db_auditor


@app.get("/auditors/", response_model=List[schemas.Auditor])
def read_auditors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    auditors = db.query(models.Auditor).offset(skip).limit(limit).all()
    return auditors


@app.post("/auditorias/", response_model=schemas.Auditoria)
def create_auditoria(
    auditoria: schemas.AuditoriaCreate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):

    email_usuario = user.claims.get("preferred_username")
    nombre_usuario = user.claims.get("name")

    print(f"Usuario autenticado: {nombre_usuario} ({email_usuario})")

    db_auditor = (
        db.query(models.Auditor).filter(models.Auditor.aud_user == auditoria.user_aud).first()
    )
    print(db_auditor)
    #auditoria.user_aud = auditoria.user_aud[: auditoria.user_aud.find("@")].lower()

    if not db_auditor:
        raise HTTPException(status_code=400, detail="Auditor no existe")

    db_auditoria = models.Auditoria(**auditoria.dict())
    db.add(db_auditoria)
    db.commit()
    db.refresh(db_auditoria)
    return db_auditoria


@app.get("/auditorias/", response_model=List[schemas.Auditoria])
def get_auditorias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    auditorias = db.query(models.Auditoria).offset(skip).limit(limit).all()
    return auditorias


@app.post("/mejoras/{op_id}/compromisos/", response_model=schemas.Compromiso)
def create_compromiso(
    compromiso: schemas.CompromisoCreate,
    op_id: int,
    db: Session = Depends(get_db),
    user=Security(azure_scheme),
):
    db_mejora = db.query(models.OpMejora).filter(models.OpMejora.id_op == op_id).first()
    if not db_mejora:
        raise HTTPException(
            status_code=404, detail="Oportunidad de mejora no encontrada"
        )

    if db_mejora.compromisos:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un compromiso para esta oportunidad de mejora",
        )

    db_compromiso = models.Compromiso(
        action=compromiso.action, deadline=compromiso.deadline, op_id=op_id
    )

    db.add(db_compromiso)
    db.commit()
    db.refresh(db_compromiso)

    return db_compromiso


@app.get("/compromisos/", response_model=List[schemas.Compromiso])
def read_compromisos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    compromisos = db.query(models.Compromiso).offset(skip).limit(limit).all()
    return compromisos


@app.get("/auditorias/{auditoria_id}", response_model=schemas.Auditoria)
def read_auditoria(auditoria_id: int, db: Session = Depends(get_db)):
    db_auditoria = (
        db.query(models.Auditoria)
        .filter(models.Auditoria.id_aud == auditoria_id)
        .first()
    )
    if db_auditoria is None:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    return db_auditoria


@app.post("/auditorias/{auditoria_id}/mejoras/", response_model=schemas.OpMejora)
def create_op_mejora(
    auditoria_id: int,
    op_mejora: schemas.OpMejoraCreate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    db_auditoria = (
        db.query(models.Auditoria)
        .filter(models.Auditoria.id_aud == auditoria_id)
        .first()
    )
    if not db_auditoria:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")

    db_mejora = models.OpMejora(description=op_mejora.description, aud_id=auditoria_id)

    db.add(db_mejora)
    db.commit()
    db.refresh(db_mejora)
    return db_mejora


@app.delete("/auditorias/{id_auditoria}", response_model=schemas.Auditoria)
def delete_auditoria(
    id_auditoria: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    item_db = (
        db.query(models.Auditoria)
        .filter(models.Auditoria.id_aud == id_auditoria)
        .first()
    )
    if not item_db:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")

    db.delete(item_db)
    db.commit()
    return item_db, {"ok": True}


@app.delete("/mejoras/{op_id}", response_model=schemas.OpMejora)
def delete_op_mejora(
    op_id: int, db: Session = Depends(get_db), user: User = Security(azure_scheme)
):
    item_db = db.query(models.OpMejora).filter(models.OpMejora.id_op == op_id).first()
    if not item_db:
        raise HTTPException(
            status_code=404, detail="Oportunidad de mejora no encontrada"
        )

    db.delete(item_db)
    db.commit()
    return item_db, {"ok": True}


@app.delete("/compromisos/{compromiso_id}", response_model=schemas.Compromiso)
def delete_compromiso(
    compromiso_id: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    item_db = (
        db.query(models.Compromiso)
        .filter(models.Compromiso.id_com == compromiso_id)
        .first()
    )
    if not item_db:
        raise HTTPException(status_code=404, detail="Compromiso no encontrado")

    db.delete(item_db)
    db.commit()
    return item_db, {"ok": True}

@app.patch("/compromisos/{compromiso_id}", response_model=schemas.Compromiso)
def update_compromiso(
    compromiso_id: int,
    compromiso_update: schemas.CompromisoUpdate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    db_compromiso = (
        db.query(models.Compromiso)
        .filter(models.Compromiso.id_com == compromiso_id)
        .first()
    )
    if not db_compromiso:
        raise HTTPException(status_code=404, detail="Compromiso no encontrado")

    update_data = compromiso_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_compromiso, key, value)

    db.add(db_compromiso)
    db.commit()
    db.refresh(db_compromiso)
    return db_compromiso

@app.get("/auditores/", response_model=List[schemas.Auditor])
def get_auditores(db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    return db.query(models.Auditor).all()

@app.get("/stats/general/", response_model=schemas.StatsData)
def get_general_stats( db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    
    total_auditorias = db.query(models.Auditoria).count()

    auditor_stats = db.query(models.Auditoria.user_aud, func.count(models.Auditoria.id_aud)).group_by(models.Auditoria.user_aud).all()

    area_stats = db.query(models.Auditoria.area, func.count(models.Auditoria.id_aud)).group_by(models.Auditoria.area).all()

    semestre = case(
    (extract('month', models.Auditoria.date_onbase) <= 6, 1),else_=2).label("semestre")

    semestre_stats = db.query(extract('year', models.Auditoria.date_onbase).label('year'),semestre,func.count(models.Auditoria.id_aud)).group_by('year', 'semestre').all()

    tema_stats = db.query(models.Auditoria.topic, func.count(models.Auditoria.id_aud)).group_by(models.Auditoria.topic).order_by(func.count(models.Auditoria.id_aud).desc()).limit(5).all()

    estado_mejora_stats = db.query(models.Compromiso.estado, func.count(models.Compromiso.id_com)).group_by(models.Compromiso.estado).all()

    return schemas.StatsData(
        total_auditorias=total_auditorias,
        por_auditor={auditor: count for auditor, count in auditor_stats},
        por_area={area: count for area, count in area_stats},
        por_semestre={f"{year}-{sem}": count for year, sem, count in semestre_stats},
        por_tema={tema: count for tema, count in tema_stats},
        por_estado_mejora={estado: count for estado, count in estado_mejora_stats},
    )