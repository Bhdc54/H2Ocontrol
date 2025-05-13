import requests

def enviar_notificacao_expo(token: str, titulo: str, corpo: str):
    url = 'https://exp.host/--/api/v2/push/send'
    payload = {
        'to': token,
        'title': titulo,
        'body': corpo,
        'sound': 'default'
    }
    headers = {
        'Content-Type': 'application/json'
    }

    print("➡️ Enviando notificação para:", token)
    response = requests.post(url, json=payload, headers=headers)
    print("📨 Resposta da API Expo:", response.status_code, response.text)
