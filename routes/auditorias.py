from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_active_auditor, get_db, inject_current_user
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/auditorias", tags=["Auditorias"])


@router.post(
    "/",
    response_model=schemas.Auditoria,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
def create_auditoria(
    auditoria: schemas.AuditoriaCreate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    inject_current_user(db=db, user=user)
    get_active_auditor(auditoria.user_aud, db)

    db_auditoria = models.Auditoria(**auditoria.dict())
    db.add(db_auditoria)
    db.commit()
    db.refresh(db_auditoria)
    return db_auditoria


@router.get(
    "/",
    response_model=List[schemas.Auditoria],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
def get_auditorias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    get_active_auditor(user.claims.get("preferred_username").split("@")[0].lower() or "unknown@domain", db)
    auditorias = db.query(models.Auditoria).offset(skip).limit(limit).all()
    return auditorias


@router.get(
    "/{auditoria_id}/",
    response_model=schemas.Auditoria,
    dependencies=[Depends(RateLimiter(times=20, seconds=60))],
)
def read_auditoria(
    auditoria_id: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    get_active_auditor(user.claims.get("preferred_username").split("@")[0].lower() or "unknown@domain", db)
    db_auditoria = (
        db.query(models.Auditoria)
        .filter(models.Auditoria.id_aud == auditoria_id)
        .first()
    )
    if db_auditoria is None:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    return db_auditoria


@router.delete(
    "/{id_auditoria}/",
    response_model=schemas.Auditoria,
    dependencies=[Depends(RateLimiter(times=1, seconds=60))],
)
def delete_auditoria(
    id_auditoria: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    inject_current_user(db=db, user=user)
    get_active_auditor(user.claims.get("preferred_username").split("@")[0].lower() or "unknown@domain", db)

    auditoria = (
        db.query(models.Auditoria)
        .filter(models.Auditoria.id_aud == id_auditoria)
        .first()
    )
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")

    db.delete(auditoria)
    db.commit()
    return auditoria
