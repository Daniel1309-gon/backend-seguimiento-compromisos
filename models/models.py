from sqlalchemy import Column, Integer, String, ForeignKey, text, Date, Text
from sqlalchemy.orm import relationship
from database import Base

class Auditor(Base):
    __tablename__ = 'auditor'

    aud_user = Column(String(10), primary_key=True, index=True)
    aud_name = Column(String(40), nullable=False)

    auditorias = relationship("Auditoria", back_populates="auditor_rel")

class Auditoria(Base):
    __tablename__ = 'auditoria'

    id_aud = Column(Integer, primary_key=True, index=True)
    
    user_aud = Column(String(10), ForeignKey('auditor.aud_user'), nullable=False)

    topic = Column(String(40), nullable=False)
    area = Column(String(50), nullable=False)
    
    date_onbase = Column(Date, 
    nullable=False,
    server_default=text("(NOW() AT TIME ZONE 'America/Bogota')::DATE")
    )
    radicate_onbase = Column(String(15), nullable=False)

    auditor_rel = relationship("Auditor", back_populates="auditorias")
    mejoras = relationship("OpMejora", back_populates="auditoria_rel", cascade="all, delete-orphan")

class OpMejora(Base):
    __tablename__ = 'op_mejora'

    id_op = Column(Integer, primary_key=True, index=True)
    
    aud_id = Column(Integer, ForeignKey('auditoria.id_aud'), nullable=False)

    description = Column(Text, nullable=False)


    auditoria_rel = relationship("Auditoria", back_populates="mejoras")
    compromisos = relationship("Compromiso", back_populates="mejora_rel", cascade="all, delete-orphan")

class Compromiso(Base):
    __tablename__ = 'compromiso'

    id_com = Column(Integer, primary_key=True, index=True)
    
    op_id = Column(Integer, ForeignKey('op_mejora.id_op'), nullable=False)

    action = Column(Text, nullable=False)

    deadline = Column(Date, 
    nullable=False,
    server_default=text("(NOW() AT TIME ZONE 'America/Bogota')::DATE + INTERVAL '2 months'")
    )
    
    estado = Column(String(20), nullable=False, server_default=text("'En proceso'"))

    mejora_rel = relationship("OpMejora", back_populates="compromisos")