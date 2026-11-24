from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core.database import obtener_bd
from models.orden import Orden as OrdenModel
from models.mecanico import Mecanico as MecanicoModel
from schemas.schemas import OrdenCreate, OrdenPatch, OrdenResponse
from typing import List

router = APIRouter(prefix="/ordenes", tags=["ordenes"])

# BUG 4 + 5 FIX: Retorna lista y usa selectinload
@router.get("/", response_model=List[OrdenResponse])
async def listar_ordenes(db: AsyncSession = Depends(obtener_bd)):
    resultado = await db.execute(
        select(OrdenModel).options(selectinload(OrdenModel.mecanico))
    )
    return resultado.scalars().all()

@router.get("/{orden_id}", response_model=OrdenResponse)
async def obtener_orden(orden_id: int, db: AsyncSession = Depends(obtener_bd)):
    resultado = await db.execute(
        select(OrdenModel).where(OrdenModel.id == orden_id).options(selectinload(OrdenModel.mecanico))
    )
    orden = resultado.scalars().first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden

# BUG 6 FIX: Valida inexistente o desactivado con 400
@router.post("/", status_code=201, response_model=OrdenResponse)
async def crear_orden(orden: OrdenCreate, db: AsyncSession = Depends(obtener_bd)):
    mecanico = await db.get(MecanicoModel, orden.mecanico_id)
    if not mecanico or not mecanico.activo:
        raise HTTPException(status_code=400, detail="Mecanico inexistente o desactivado")

    nueva_orden = OrdenModel(**orden.model_dump())
    db.add(nueva_orden)
    await db.commit()
    await db.refresh(nueva_orden)
    return nueva_orden

# BUG 7 FIX: exclude_unset=True para no borrar datos
@router.patch("/{orden_id}", response_model=OrdenResponse)
async def actualizar_orden(orden_id: int, datos: OrdenPatch, db: AsyncSession = Depends(obtener_bd)):
    orden = await db.get(OrdenModel, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(orden, campo, valor)

    await db.commit()
    await db.refresh(orden)
    return orden

# BUG 8 FIX: await + commit en DELETE
@router.delete("/{orden_id}")
async def eliminar_orden(orden_id: int, db: AsyncSession = Depends(obtener_bd)):
    orden = await db.get(OrdenModel, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    await db.delete(orden)
    await db.commit()
    return {"detail": "Orden eliminada"}