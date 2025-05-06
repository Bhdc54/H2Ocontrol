import os
from google.cloud import firestore

# Autenticar com as credenciais
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firebase_config.json"

# Inicializar cliente Firestore
db = firestore.Client()
