import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    try:
        # Verifica se o Firebase já foi inicializado
        if not firebase_admin._apps:
            # Carrega as credenciais
            cred = credentials.Certificate("firebase_config.json")
            
            # Inicializa o Firebase com configurações explícitas
            firebase_admin.initialize_app(cred, {
                'projectId': cred.project_id,
                'storageBucket': f"{cred.project_id}.appspot.com"
            })
            
            logger.info("Firebase inicializado com sucesso")
            return True
        return False
    except FileNotFoundError:
        logger.error("Arquivo de configuração do Firebase não encontrado")
        raise
    except ValueError as ve:
        logger.error(f"Erro no formato do arquivo de configuração: {str(ve)}")
        raise
    except FirebaseError as fe:
        logger.error(f"Erro ao inicializar Firebase: {str(fe)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise

# Inicializa o Firebase ao importar o módulo
try:
    initialize_firebase()
    db = firestore.client()
except Exception:
    # Define db como None para tratamento em outros módulos
    db = None
    logger.warning("Firestore não disponível - operações de banco de dados falharão")

# Exporta a instância do Firestore
def get_firestore_client():
    if db is None:
        raise RuntimeError("Firestore não foi inicializado corretamente")
    return db