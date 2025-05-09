import firebase_admin
from firebase_admin import credentials, messaging

# Inicializar Firebase apenas uma vez
def inicializar_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("C:\Users\hbrun\H2OControl\firebase_config.json")
        firebase_admin.initialize_app(cred)

# Enviar notificação
def enviar_notificacao(token: str, titulo: str, corpo: str):
    inicializar_firebase()

    mensagem = messaging.Message(
        notification=messaging.Notification(
            title=titulo,
            body=corpo
        ),
        token=token
    )

    resposta = messaging.send(mensagem)
    print("Notificação enviada:", resposta)
