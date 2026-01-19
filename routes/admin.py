from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from typing import List
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db, get_current_admin
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/logs/", 
    response_model=List[schemas.SystemLog], 
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
    )
@cache(expire=10)
def get_system_logs(skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    userAdmin: User = Depends(get_current_admin), 
    user = Security(azure_scheme)
    ):
    logs = db.query(models.SystemLog).order_by(models.SystemLog.id.desc()).offset(skip).limit(limit).all()
    return logs