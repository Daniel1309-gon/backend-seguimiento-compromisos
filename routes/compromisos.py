from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, inject_current_user
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache

router = APIRouter(tags=["Compromisos"])

@router.post("/mejoras/{op_id}/compromisos/", response_model=schemas.Compromiso, dependencies=[Depends(RateLimiter(times=5, seconds=60))])

def create_compromiso(
    compromiso: schemas.CompromisoCreate,
    op_id: int,
    db: Session = Depends(get_db),
    user=Security(azure_scheme)
):
    inject_current_user(db=db, user=user)
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


@router.get("/compromisos/", response_model=List[schemas.Compromiso], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def read_compromisos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    compromisos = db.query(models.Compromiso).offset(skip).limit(limit).all()
    return compromisos


@router.delete("/compromisos/{compromiso_id}/", response_model=schemas.Compromiso, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def delete_compromiso(
    compromiso_id: int,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme)
):
    inject_current_user(db=db, user=user)
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

@router.patch("/compromisos/{compromiso_id}/", response_model=schemas.Compromiso, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def update_compromiso(
    compromiso_id: int,
    compromiso_update: schemas.CompromisoUpdate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme)
):
    inject_current_user(db=db, user=user)
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