# dependencies.py
from fastapi import Depends, HTTPException, Security
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi_azure_auth.user import User
from database import SessionLocal
from config import settings
from auth import azure_scheme

# Configuración de Admins
ADMIN_EMAILS = [settings.ADMIN_USER_AUDITOR, settings.ADMIN_USER_PASANTE]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_admin(db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    # Lógica segura para obtener el username
    full_email = user.claims.get("preferred_username") or "unknown@domain"
    
    if full_email.lower() not in [a.lower() for a in ADMIN_EMAILS]:
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    

    return {'username': full_email.split("@")[0]}

def inject_current_user(db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    full_email = user.claims.get("preferred_username") or "unknown@domain"
    username = full_email.split("@")[0]
    
    # Inyección de contexto para PostgreSQL (Logs)
    db.execute(
        text("SELECT set_config('app.current_user', :app_user, true)"), 
        {'app_user': username}
    )
    return username