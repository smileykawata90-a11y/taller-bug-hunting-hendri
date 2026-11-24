from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    placa = Column(String(6), index=True, nullable=False)
    modelo = Column(String(50), nullable=False)
    falla_reportada = Column(String(255))
    estado = Column(String(20), default="En diagnóstico")
    costo_reparacion = Column(Float, default=0.0)
    mecanico_id = Column(Integer, ForeignKey("mecanicos.id"), nullable=False)

    mecanico = relationship("Mecanico", back_populates="ordenes")
    # no bug