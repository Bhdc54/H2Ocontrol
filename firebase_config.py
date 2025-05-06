import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa o Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# Cria o cliente Firestore
db = firestore.client()