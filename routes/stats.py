from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from sqlalchemy import case, func, extract
from fastapi_azure_auth.user import User
import models.models as models
import schemas.schemas as schemas
from auth import azure_scheme
from dependencies import get_db
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/stats", tags=["Estadísticas"])

@router.get("/general/", response_model=schemas.StatsData, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@cache(expire=60)
def get_general_stats( db: Session = Depends(get_db), user: User = Security(azure_scheme)):
    
    total_auditorias = db.query(models.Auditoria).count()

    auditor_stats = db.query(models.Auditoria.user_aud, func.count(models.Auditoria.id_aud)).group_by(models.Auditoria.user_aud).all()

    area_stats = db.query(models.Auditoria.area, func.count(models.Auditoria.id_aud)).group_by(models.Auditoria.area).all()

    semestre = case(
    (extract('month', models.Auditoria.date_onbase) <= 6, 1),else_=2).label("semestre")

    semestre_stats = db.query(extract('year', models.Auditoria.date_onbase).label('year'),semestre,func.count(models.Auditoria.id_aud)).group_by('year', 'semestre').all()

    tema_stats = db.query(models.Auditoria.topic, func.count(models.Auditoria.id_aud)).group_by(models.Auditoria.topic).order_by(func.count(models.Auditoria.id_aud).desc()).limit(5).all()

    estado_mejora_stats = db.query(models.Compromiso.estado, func.count(models.Compromiso.id_com)).group_by(models.Compromiso.estado).all()

    return schemas.StatsData(
        total_auditorias=total_auditorias,
        por_auditor={auditor: count for auditor, count in auditor_stats},
        por_area={area: count for area, count in area_stats},
        por_semestre={f"{year}-{sem}": count for year, sem, count in semestre_stats},
        por_tema={tema: count for tema, count in tema_stats},
        por_estado_mejora={estado: count for estado, count in estado_mejora_stats},
    )