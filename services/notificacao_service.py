import requests

def enviar_notificacao_expo(expo_token: str, titulo: str, mensagem: str):
    url = 'https://exp.host/--/api/v2/push/send'
    payload = {
        'to': expo_token,
        'title': titulo,
        'body': mensagem,
        'sound': 'default'
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)
    print('Resposta:', response.text)
    return response.json()