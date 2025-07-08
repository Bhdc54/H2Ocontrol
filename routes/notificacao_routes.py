from fastapi import APIRouter
from firebase_admin import firestore
import requests

router = APIRouter(
    prefix="/notificacoes",
    tags=["Notificações"]
)

db = firestore.client()

def enviar_notificacao_expo(expo_token: str, titulo: str, mensagem: str):
    url = 'https://exp.host/--/api/v2/push/send'
    payload = {
        'to': expo_token,
        'title': titulo,
        'body': mensagem,
        'sound': 'default',
        'priority': 'high'
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"✅ Notificação enviada: {mensagem}")
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao enviar notificação: {e}")
        return {'error': str(e)}

def ativar_ventoinha():
    try:
        response = requests.get("https://sua-api-ventoinha.railway.app/ligar")  # 🔁 Substituir pela real
        print("🌬 Ventoinha ativada:", response.status_code)
    except Exception as e:
        print("❌ Erro ao ativar ventoinha:", e)

@router.get("/verificar-temperatura")
async def verificar_temperatura():
    aquarios = db.collection("aquarios").stream()

    for aq_doc in aquarios:
        aquario = aq_doc.to_dict()
        usuario_id = aquario.get("usuarioID")
        sensor_id = aquario.get("sensorID")
        temp_min = aquario.get("tempMinima")
        temp_max = aquario.get("tempMaxima")

        if not all([usuario_id, sensor_id, temp_min, temp_max]):
            continue

        # Busca dados do sensor
        sensor_doc = db.collection("sensores").document(sensor_id).get()
        if not sensor_doc.exists:
            continue

        sensor_data = sensor_doc.to_dict()
        temperatura = sensor_data.get("temperatura")

        if temperatura is not None and (temperatura < temp_min or temperatura > temp_max):
            print(f"⚠ Temperatura fora do limite: {temperatura}°C")

            user_doc = db.collection("usuarios").document(usuario_id).get()
            if user_doc.exists:
                expo_token = user_doc.to_dict().get("pushToken")

                if expo_token:
                    enviar_notificacao_expo(
                        expo_token,
                        "Alerta de Temperatura",
                        f"A temperatura do aquário está em {temperatura}°C!"
                    )

            ativar_ventoinha()

    return {"status": "Verificação concluída"}
