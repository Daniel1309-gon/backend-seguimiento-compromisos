from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

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

class OpMejoraBase(BaseModel):
    description: str

class OpMejoraCreate(OpMejoraBase):
    pass

class OpMejora(OpMejoraBase):
    id_op: int
    aud_id: int
    compromisos: List[Compromiso] = []

    class Config:
        from_attribute = True

class AuditoriaBase(BaseModel):
    topic: str
    area: str
    radicate_onbase: str

class AuditoriaCreate(AuditoriaBase):
    user_aud: str

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