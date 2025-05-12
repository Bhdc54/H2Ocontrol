import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
from dotenv import load_dotenv
from firebase_admin import messaging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    try:
        if not firebase_admin._apps:
            # 1. Verifica se existe variável de ambiente com JSON
            firebase_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

            if firebase_json:
                logger.info("Inicializando Firebase com variável de ambiente")
                cred_info = json.loads(firebase_json)
                cred = credentials.Certificate(cred_info)
            else:
                logger.info("Inicializando Firebase com arquivo local firebase_config.json")
                cred = credentials.Certificate("firebase_config.json")

            firebase_admin.initialize_app(cred, {
                'projectId': cred.project_id,
                'storageBucket': f"{cred.project_id}.appspot.com"
            })

            logger.info("Firebase inicializado com sucesso")
            return True

        return False

    except FileNotFoundError:
        logger.error("Arquivo firebase_config.json não encontrado")
        raise
    except ValueError as ve:
        logger.error(f"Erro no formato do JSON: {str(ve)}")
        raise
    except FirebaseError as fe:
        logger.error(f"Erro ao inicializar Firebase: {str(fe)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise

# Executa a inicialização e cria o cliente Firestore
try:
    initialize_firebase()
    db = firestore.client()
except Exception:
    db = None
    logger.warning("Firestore não disponível - verifique as credenciais")

def get_firestore_client():
    if db is None:
        raise RuntimeError("Firestore não foi inicializado corretamente")
    return db

def send_push_notification(token: str, title: str, body: str):
    # Cria a mensagem com título e corpo
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )

    # Envia a notificação
    try:
        response = messaging.send(message)
        print("Notificação enviada com sucesso:", response)
        return response
    except Exception as e:
        print("Erro ao enviar notificação:", str(e))
        raise