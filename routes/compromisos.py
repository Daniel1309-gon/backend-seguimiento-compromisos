from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from workalendar.america import Colombia
from typing import List
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, inject_current_user
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache

router = APIRouter(tags=["Compromisos"])


def get_business_day_target(days: int) -> date:
    calendar = Colombia()
    current_day = date.today()
    added_days = 0
    while added_days < days:
        current_day += timedelta(days=1)
        if calendar.is_working_day(current_day):
            added_days += 1
    return current_day

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


@router.get("/compromisos/en-proceso/", response_model=List[schemas.CompromisoEnProceso], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def read_compromisos_en_proceso(
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme)
):
    compromisos = (
        db.query(
            models.Compromiso,
            models.OpMejora.description.label("op_description"),
            models.Auditoria.id_aud,
            models.Auditoria.topic,
            models.Auditoria.area,
            models.Auditoria.radicate_onbase,
        )
        .join(models.OpMejora, models.Compromiso.op_id == models.OpMejora.id_op)
        .join(models.Auditoria, models.OpMejora.aud_id == models.Auditoria.id_aud)
        .filter(models.Compromiso.estado == "En proceso")
        .order_by(models.Compromiso.deadline.asc())
        .all()
    )

    return [
        schemas.CompromisoEnProceso(
            id_com=compromiso.id_com,
            op_id=compromiso.op_id,
            action=compromiso.action,
            deadline=compromiso.deadline,
            estado=compromiso.estado,
            op_description=op_description,
            aud_id=id_aud,
            topic=topic,
            area=area,
            radicate_onbase=radicate_onbase,
        )
        for compromiso, op_description, id_aud, topic, area, radicate_onbase in compromisos
    ]


@router.get("/compromisos/en-proceso/proximos/", response_model=List[schemas.CompromisoEnProceso], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def read_compromisos_en_proceso_proximos(
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme)
):
    today = date.today()
    next_month = today + timedelta(days=30)

    compromisos = (
        db.query(
            models.Compromiso,
            models.OpMejora.description.label("op_description"),
            models.Auditoria.id_aud,
            models.Auditoria.topic,
            models.Auditoria.area,
            models.Auditoria.radicate_onbase,
        )
        .join(models.OpMejora, models.Compromiso.op_id == models.OpMejora.id_op)
        .join(models.Auditoria, models.OpMejora.aud_id == models.Auditoria.id_aud)
        .filter(models.Compromiso.estado == "En proceso")
        .filter(models.Compromiso.deadline >= today)
        .filter(models.Compromiso.deadline <= next_month)
        .order_by(models.Compromiso.deadline.asc())
        .all()
    )

    return [
        schemas.CompromisoEnProceso(
            id_com=compromiso.id_com,
            op_id=compromiso.op_id,
            action=compromiso.action,
            deadline=compromiso.deadline,
            estado=compromiso.estado,
            op_description=op_description,
            aud_id=id_aud,
            topic=topic,
            area=area,
            radicate_onbase=radicate_onbase,
        )
        for compromiso, op_description, id_aud, topic, area, radicate_onbase in compromisos
    ]


@router.get("/compromisos/en-proceso/pronto_vencimiento/", response_model=List[schemas.CompromisoEnProceso], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@cache(expire=21600)
def read_compromisos_pronto_vencimiento(
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme)
):
    target_date = get_business_day_target(7)
    compromisos = (
        db.query(
            models.Compromiso,
            models.OpMejora.description,
            models.Auditoria.id_aud,
            models.Auditoria.topic,
            models.Auditoria.area,
            models.Auditoria.radicate_onbase,
        )
        .join(models.OpMejora, models.Compromiso.op_id == models.OpMejora.id_op)
        .join(models.Auditoria, models.OpMejora.aud_id == models.Auditoria.id_aud)
        .filter(models.Compromiso.estado == "En proceso")
        .filter(models.Compromiso.deadline <= target_date)
        .order_by(models.Compromiso.deadline.asc())
        .all()
    )


    return [
        schemas.CompromisoEnProceso(
            id_com=compromiso.id_com,
            op_id=compromiso.op_id,
            action=compromiso.action,
            deadline=compromiso.deadline,
            estado=compromiso.estado,
            op_description=op_description,
            aud_id=id_aud,
            topic=topic,
            area=area,
            radicate_onbase=radicate_onbase,
        )
        for compromiso, op_description, id_aud, topic, area, radicate_onbase in compromisos
    ]


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
