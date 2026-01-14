from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, get_current_admin

router = APIRouter(prefix="/auditorias", tags=["Auditorias"])


@router.get("/", response_model=List[schemas.Auditoria])
def get_auditorias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    auditorias = db.query(models.Auditoria).offset(skip).limit(limit).all()
    return auditorias

@router.get("/{auditoria_id}", response_model=schemas.Auditoria)
def read_auditoria(auditoria_id: int, db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    db_auditoria = (
        db.query(models.Auditoria)
        .filter(models.Auditoria.id_aud == auditoria_id)
        .first()
    )
    if db_auditoria is None:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    return db_auditoria




@router.delete("/{id_auditoria}", response_model=schemas.Auditoria)
def delete_auditoria(
    id_auditoria: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
    current_admin_username: str = Depends(get_current_admin)
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