from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# 🔥 Configuração do Firebase
firebase_config = os.getenv("FIREBASE_CONFIG")

if not firebase_config:
    raise ValueError("Variável FIREBASE_CONFIG não encontrada!")

cred = credentials.Certificate(json.loads(firebase_config))
firebase_admin.initialize_app(cred)
db = firestore.client()  # 📦 Conexão com o Firestore

# 🚀 Cria a aplicação FastAPI
app = FastAPI()

# 📦 Modelos de dados
class SensorData(BaseModel):
    temperatura: float
    umidade: float
    distancia: float
    acao_ventoinha: str = None

class VentoinhaState(BaseModel):
    estado: str  # "ligado" ou "desligado"

# 💾 Armazenamento em memória
dados_sensores: List[SensorData] = []
ventoinha_estado = "desligado"

# 🔧 Função auxiliar
def set_ventoinha_estado(novo_estado: str):
    global ventoinha_estado
    if novo_estado in ["ligado", "desligado"]:
        ventoinha_estado = novo_estado
        # Salva no Firestore (opcional)
        db.collection("estado").document("ventoinha").set({"estado": ventoinha_estado})
    return ventoinha_estado

# 🌐 Rotas da API
@app.get("/")
async def health_check():
    return {"status": "online", "app": "H2O Control"}

@app.post("/sensores")
async def receber_dados(data: SensorData):
    try:
        dados_sensores.append(data)
        
        # Salva no Firestore (opcional)
        doc_ref = db.collection("leituras").document()
        doc_ref.set({
            "temperatura": data.temperatura,
            "umidade": data.umidade,
            "distancia": data.distancia,
            "timestamp": datetime.now().isoformat()
        })
        
        if data.acao_ventoinha:
            set_ventoinha_estado(data.acao_ventoinha)
            
        return {"status": "sucesso", "ventoinha": ventoinha_estado}
    
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}

@app.get("/sensores")
async def listar_dados(limit: int = 10):
    return {
        "dados": dados_sensores[-limit:],
        "total": len(dados_sensores),
        "firestore": db.collection("leituras").limit(limit).get()
    }

@app.get("/ventoinha")
async def ver_estado():
    return {"estado": ventoinha_estado}

@app.post("/ventoinha")
async def alterar_estado(estado: VentoinhaState):
    if estado.estado in ["ligado", "desligado"]:
        set_ventoinha_estado(estado.estado)
        return {"mensagem": f"Ventoinha {ventoinha_estado}"}
    return {"erro": "Estado inválido"}