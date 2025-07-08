import requests

def enviar_notificacao(push_token: str, titulo: str, mensagem: str):
    url = "https://exp.host/--/api/v2/push/send"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "to": push_token,
        "title": titulo,
        "body": mensagem,
        "sound": "default"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao enviar notificação: {response.status_code} - {response.text}")
    else:
        print("Notificação enviada com sucesso:", response.json())
