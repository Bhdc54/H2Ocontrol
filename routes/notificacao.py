from fastapi import APIRouter
from pydantic import BaseModel
from firebase_config import send_push_notification

router = APIRouter(prefix="/notificacao", tags=["Notificações"])

# Simples armazenamento temporário (em memória)
tokens_registrados = {}

# Modelo para envio de notificação
class NotificationRequest(BaseModel):
    token: str
    title: str
    body: str

# Modelo para registro de token
class TokenRequest(BaseModel):
    token: str
    uid: str  # UID do usuário autenticado no Firebase

# Endpoint: Enviar notificação
@router.post("/enviar")
async def enviar_notificacao(data: NotificationRequest):
    try:
        response = send_push_notification(data.token, data.title, data.body)
        return {"message": "Notificação enviada com sucesso!", "firebase_response": response}
    except Exception as e:
        return {"error": str(e)}

# Endpoint: Registrar token do dispositivo
@router.post("/registrar")
async def registrar_token(data: TokenRequest):
    tokens_registrados[data.uid] = data.token
    print(f"Token registrado para UID {data.uid}: {data.token}")
    return {"message": "Token registrado com sucesso"}
