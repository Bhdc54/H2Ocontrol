import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
SERVICE_ACCOUNT_FILE = "firebase_admin.json"  # ⚠️ Coloque o arquivo na raiz do projeto

# Substitua com o token FCM do seu dispositivo/app mobile
TOKEN_DISPOSITIVO = "COLE_AQUI_O_TOKEN_FCM_DO_APP"

def enviar_notificacao_fcm(titulo: str, corpo: str, token: str = TOKEN_DISPOSITIVO):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    access_token = credentials.token

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": titulo,
                "body": corpo
            }
        }
    }

    url = f"https://fcm.googleapis.com/v1/projects/{credentials.project_id}/messages:send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8",
    }

    response = requests.post(url, headers=headers, data=json.dumps(message))
    print(f"📤 Notificação enviada. Status: {response.status_code}")
    print(response.text)
    return response.status_code, response.text
