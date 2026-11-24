from pydantic import BaseModel, Field
from typing import Optional, List

class MecanicoCreate(BaseModel):
    nombre_completo: str
    especialidad: str

class MecanicoResponse(MecanicoCreate): 
    id: int
    activo: bool
    # BUG 1: BORRADO - esto causaba el bucle infinito
    # ordenes: List["OrdenResponse"] = []
    # Orden -> Mecanico -> Orden -> Mecanico  nunca terminaba

    model_config = {"from_attributes": True}

class OrdenCreate(BaseModel):
    placa: str = Field(..., min_length=5, max_length=6)
    modelo: str
    falla_reportada: str
    mecanico_id: int

class OrdenPatch(BaseModel):
    estado: Optional[str] = None
    costo_reparacion: Optional[float] = Field(None, ge=0)
    falla_reportada: Optional[str] = None

class OrdenResponse(OrdenCreate):
    id: int
    estado: str
    costo_reparacion: float
    mecanico: Optional[MecanicoResponse] = None

    # BUG 2: FALTABA esto, sin esto no puede convertir el objeto de la BD a JSON
    model_config = {"from_attributes": True}