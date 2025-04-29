from fastapi import FastAPI
from api.routers import sensores, ventoinha
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# 🔧 Lê a configuração do Firebase do ambiente (Railway)
firebase_config = os.getenv("FIREBASE_CONFIG")

if firebase_config is None:
    raise Exception("Variável de ambiente FIREBASE_CONFIG não encontrada!")

# 🛠️ Converte o JSON da variável de ambiente em dicionário
cred_dict = json.loads(firebase_config)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# 📦 Inicializa o Firestore
db = firestore.client()

# 🚀 Inicializa o app FastAPI
app = FastAPI()

# 🔗 Inclui os routers
app.include_router(sensores.router)
app.include_router(ventoinha.router)
