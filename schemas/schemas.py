from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class CompromisoBase(BaseModel):
    action: str
    estado: Optional[str] = Field(default="En proceso")

class CompromisoCreate(CompromisoBase):
    deadline: Optional[date] = None

class Compromiso(CompromisoBase):
    id_com: int
    op_id: int
    deadline: date

    class Config:
        from_attribute = True


class OpMejoraCreate(BaseModel):
    description: str

class OpMejora(OpMejoraCreate):
    id_op: int
    aud_id: int
    compromisos: Optional[Compromiso] = None

    class Config:
        from_attribute = True

class AuditoriaBase(BaseModel):
    topic: str
    area: str
    radicate_onbase: str
    user_aud: str

class AuditoriaCreate(AuditoriaBase):
    user_aud: str
    date_onbase: date

class Auditoria(AuditoriaBase):
    id_aud: int
    user_aud: str
    date_onbase: date
    mejoras: List[OpMejora] = []

    class Config:
        from_attribute = True

class AuditorBase(BaseModel):
    aud_user: str
    aud_name: str

class AuditorCreate(AuditorBase):
    pass

class Auditor(AuditorBase):
    auditorias: List[Auditoria] = []

    class Config:
        from_attribute = True


class CompromisoUpdate(BaseModel):
    action: Optional[str] = None
    deadline: Optional[date] = None
    estado: Optional[str] = None


class StatsData(BaseModel):
    total_auditorias: int
    por_auditor: dict[str, int]
    por_area: dict[str, int]
    por_semestre: dict[str, int]
    por_tema: dict[str, int]
    por_estado_mejora: dict[str, int]

class SystemLog(BaseModel):
    id: int
    table_name: str
    action: str
    record_id: str
    old_data: Optional[str] = None
    new_data: Optional[str] = None
    changed_at: datetime
    app_user: Optional[str] = None
    db_user: str

    class Config:
        from_attributes = True

class SeguimientoCreate(BaseModel):
    observation: str = Field(..., min_length=1, max_length=1000)

class Seguimiento(SeguimientoCreate):
    id_seg: int
    com_id: int
    created_by: str
    created_at: date
    

    class Config:
        from_attributes = True