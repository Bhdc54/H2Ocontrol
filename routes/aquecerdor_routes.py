from fastapi import APIRouter
from models.aquecedor_models import AquecedorState
from services.aquecedor_service import set_aquecedor_estado, get_aquecedor_estado

router = APIRouter(prefix="/aquecedor", tags=["Aquecedor"])

@router.get("/")
async def obter_estado_aquecedor():
    return {"estado": get_aquecedor_estado()}

@router.post("/")
async def definir_estado_aquecedor(estado: AquecedorState):
    if estado.estado in ["ligado", "desligado"]:
        set_aquecedor_estado(estado.estado)
        return {"mensagem": f"Aquecedor agora está {get_aquecedor_estado()}"}
    else:
        return {"erro": "Estado inválido! Use 'ligado' ou 'desligado'."}
