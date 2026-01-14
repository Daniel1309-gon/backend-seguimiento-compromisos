from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, get_current_admin

router = APIRouter(tags=["Mejoras"])

@router.post("/auditorias/{auditoria_id}/mejoras/", response_model=schemas.OpMejora)
def create_op_mejora(
    auditoria_id: int,
    op_mejora: schemas.OpMejoraCreate,
    db: Session = Depends(get_db),
    user: User = Security(azure_scheme),
    current_admin_username: str = Depends(get_current_admin)
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

@router.delete("/mejoras/{op_id}", response_model=schemas.OpMejora)
def delete_op_mejora(
    op_id: int, db: Session = Depends(get_db), user: User = Security(azure_scheme), current_admin_username: str = Depends(get_current_admin)
):
    item_db = db.query(models.OpMejora).filter(models.OpMejora.id_op == op_id).first()
    if not item_db:
        raise HTTPException(
            status_code=404, detail="Oportunidad de mejora no encontrada"
        )

    db.delete(item_db)
    db.commit()
    return item_db, {"ok": True}