from fastapi import APIRouter

router = APIRouter()

@router.get("/notificacoes")
async def listar_notificacoes():
    return {"mensagem": "Nenhuma notificação"}
