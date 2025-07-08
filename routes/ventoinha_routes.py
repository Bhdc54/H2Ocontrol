from fastapi import APIRouter
from services import ventoinha_service

router = APIRouter(
    prefix="",
    tags=["Ventoinha"]
)

@router.get("/ligar")
async def ligar_ventoinha():
    ventoinha_service.set_ventoinha_estado("ligado")
    return {"status": "Ventoinha ligada com sucesso"}

@router.get("/desligar")
async def desligar_ventoinha():
    ventoinha_service.set_ventoinha_estado("desligado")
    return {"status": "Ventoinha desligada com sucesso"}

@router.get("/estado")
async def estado_ventoinha():
    estado = ventoinha_service.get_ventoinha_estado()
    return {"estado": estado}
