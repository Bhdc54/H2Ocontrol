import firebase_admin
from firebase_admin import credentials, firestore

# Substitua pelo caminho correto do seu JSON
cred = credentials.Certificate("C:\Users\hbrun\H2OControl\firebase_config.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
