from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi_azure_auth.user import User
from typing import List
from sqlalchemy.orm import Session
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, inject_current_user
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/follow_up", tags=["Seguimiento"])

@router.post("/{id_com}/comments/", response_model=schemas.Seguimiento, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_seguimiento(
    id_com: int,
    seguimiento: schemas.SeguimientoCreate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    inject_current_user(db=db, user=user)

    db_com = db.query(models.Compromiso).filter(models.Compromiso.id_com == id_com).first()
    if not db_com:
        raise HTTPException(status_code=404, detail="Compromiso no encontrado")

    auditors = db.query(models.Auditor).all()

    auditor_user = user.preferred_username.split("@")[0].lower()

    if auditor_user not in [aud.aud_user for aud in auditors]:
        raise HTTPException(status_code=403, detail="Usuario no autorizado para crear seguimientos")

    db_seguimiento = models.Seguimiento(
        com_id=id_com,
        observation=seguimiento.observation,
        created_by=auditor_user
    )
    db.add(db_seguimiento)
    db.commit()
    db.refresh(db_seguimiento)
    return db_seguimiento

@router.get("/{id_com}/comments/", response_model=List[schemas.Seguimiento], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def get_seguimientos(
    id_com: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    db_com = db.query(models.Compromiso).filter(models.Compromiso.id_com == id_com).first()
    if not db_com:
        raise HTTPException(status_code=404, detail="Compromiso no encontrado")

    seguimientos = db.query(models.Seguimiento).filter(models.Seguimiento.com_id == id_com).order_by(models.Seguimiento.created_at.desc()).all()
    return seguimientos

@router.delete("/comments/{id_seg}/", response_model=schemas.Seguimiento, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
def delete_seguimiento(
    id_seg: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
):
    inject_current_user(db=db, user=user)

    db_seguimiento = db.query(models.Seguimiento).filter(models.Seguimiento.id_seg == id_seg).first()
    if not db_seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
    
    auditors = db.query(models.Auditor).all()

    auditor_user = user.preferred_username.split("@")[0].lower()

    if auditor_user not in [aud.aud_user for aud in auditors]:
        raise HTTPException(status_code=403, detail="Usuario no autorizado para eliminar seguimientos")

    db.delete(db_seguimiento)
    db.commit()
    return db_seguimiento