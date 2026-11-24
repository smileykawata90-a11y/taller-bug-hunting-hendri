from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import obtener_bd
from models.mecanico import Mecanico as MecanicoModel
from schemas.schemas import MecanicoCreate, MecanicoResponse
from typing import List

router = APIRouter(prefix="/mecanicos", tags=["mecanicos"])

# BUG 10 FIX: Solo activos
@router.get("/", response_model=List[MecanicoResponse])
async def listar_mecanicos(db: AsyncSession = Depends(obtener_bd)):
    resultado = await db.execute(
        select(MecanicoModel).where(MecanicoModel.activo == True)
    )
    return resultado.scalars().all()

@router.get("/{mecanico_id}", response_model=MecanicoResponse)
async def obtener_mecanico(mecanico_id: int, db: AsyncSession = Depends(obtener_bd)):
    mecanico = await db.get(MecanicoModel, mecanico_id)
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")
    return mecanico

@router.post("/", status_code=201, response_model=MecanicoResponse)
async def crear_mecanico(mecanico: MecanicoCreate, db: AsyncSession = Depends(obtener_bd)):
    nuevo = MecanicoModel(**mecanico.model_dump())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

# BUG 9 FIX: Soft-delete + commit, no borra físico
@router.delete("/{mecanico_id}")
async def desactivar_mecanico(mecanico_id: int, db: AsyncSession = Depends(obtener_bd)):
    mecanico = await db.get(MecanicoModel, mecanico_id)
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    mecanico.activo = False
    await db.commit()
    return {"detail": "Mecanico desactivado"}