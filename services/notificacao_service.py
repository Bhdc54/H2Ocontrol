import httpx

async def enviar_notificacao_expo(push_token: str, titulo: str, mensagem: str):
    url = "https://exp.host/--/api/v2/push/send"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "to": push_token,
        "sound": "default",
        "title": titulo,
        "body": mensagem
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()
