from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, get_current_admin

router = APIRouter(
    prefix="/auditors",
    tags=["Auditores"]
)

@router.post("/", response_model=schemas.Auditor)
def create_auditor(auditor: schemas.AuditorCreate, db: Session = Depends(get_db), user: User = Security(azure_scheme), userAdmin: User = Depends(get_current_admin), current_admin_username: str = Depends(get_current_admin)):
    db_auditor = models.Auditor(**auditor.dict())
    db.add(db_auditor)
    db.commit()
    db.refresh(db_auditor)
    return db_auditor

@router.delete("/{aud_user}", response_model=schemas.Auditor)
def delete_auditor(aud_user: str, db: Session = Depends(get_db), userAdmin: User = Depends(get_current_admin), user: User = Security(azure_scheme), current_admin_username: str = Depends(get_current_admin)):
    auditor_db = db.query(models.Auditor).filter(models.Auditor.aud_user == aud_user).first()
    if not auditor_db:
        raise HTTPException(status_code=404, detail="Auditor no encontrado")

    db.delete(auditor_db)
    db.commit()
    return auditor_db


@router.get("/", response_model=List[schemas.Auditor])
def read_auditors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    auditors = db.query(models.Auditor).offset(skip).limit(limit).all()
    return auditors