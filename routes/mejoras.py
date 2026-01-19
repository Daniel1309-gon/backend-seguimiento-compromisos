from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, inject_current_user
from fastapi_limiter.depends import RateLimiter

router = APIRouter(tags=["Mejoras"])

@router.post("/auditorias/{auditoria_id}/mejoras/", response_model=schemas.OpMejora, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_op_mejora(
    auditoria_id: int,
    op_mejora: schemas.OpMejoraCreate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme)
):
    inject_current_user(db=db, user=user)
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

@router.delete("/mejoras/{op_id}", response_model=schemas.OpMejora, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def delete_op_mejora(
    op_id: int, 
    db: Session = Depends(get_db), 
    user: User = Security(azure_scheme)
):
    inject_current_user(db=db, user=user)
    item_db = db.query(models.OpMejora).filter(models.OpMejora.id_op == op_id).first()
    if not item_db:
        raise HTTPException(
            status_code=404, detail="Oportunidad de mejora no encontrada"
        )

    db.delete(item_db)
    db.commit()
    return item_db, {"ok": True}