from fastapi import APIRouter
from services.notificacao_fcm import enviar_notificacao

router = APIRouter()

@router.post("/notificacoes/enviar")
def notificar(token: str, titulo: str, corpo: str):
    resposta = enviar_notificacao(token, titulo, corpo)
    return {"mensagem": "Notificação enviada", "resposta": resposta}
