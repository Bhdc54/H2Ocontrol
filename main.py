from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = FastAPI()

# Iniciar o Firebase com tratamento de erro
db = None
"""try:
    # Carrega config do Firebase a partir de variável de ambiente (recomendado no Railway)
    firebase_config = json.loads(os.environ["FIREBASE_CONFIG_JSON"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("🔥 Conectado ao Firestore!")
except Exception as e:
    print("⚠️ Falha ao conectar ao Firebase:", e)"""

# Modelo de dados que o Arduino vai enviar
class SensorData(BaseModel):
    temperatura: float
    umidade: float
    distancia: float
    acao_ventoinha: Optional[str] = None

# Modelo para receber o estado da ventoinha
class VentoinhaState(BaseModel):
    estado: str  # "ligado" ou "desligado"

# Lista local para armazenar os dados recebidos
dados_sensores: List[SensorData] = []

# Estado atual da ventoinha
ventoinha_estado = "desligado"

# Função para definir o estado da ventoinha
def set_ventoinha_estado(novo_estado: str):
    global ventoinha_estado
    if novo_estado in ["ligado", "desligado"]:
        ventoinha_estado = novo_estado
        print(f"✅ Ventoinha agora está {ventoinha_estado}")
    else:
        print(f"❌ Estado inválido recebido: {novo_estado}")

@app.post("/sensores")
async def receber_dados(data: SensorData):
    try:
        dados_sensores.append(data)

        print(f"📡 Dados recebidos - Temperatura: {data.temperatura}, Umidade: {data.umidade}, Distância: {data.distancia}")

        if data.acao_ventoinha == "ligar":
            set_ventoinha_estado("ligado")
        elif data.acao_ventoinha == "desligar":
            set_ventoinha_estado("desligado")

        # Envia para Firestore se conectado
        if db:
            db.collection("leituras").add({
                "temperatura": data.temperatura,
                "umidade": data.umidade,
                "distancia": data.distancia,
                "acao_ventoinha": data.acao_ventoinha,
                "timestamp": datetime.now().isoformat()
            })

        return {
            "status": "sucesso",
            "timestamp": datetime.now().isoformat(),
            "ventoinha_estado_atual": ventoinha_estado
        }

    except Exception as e:
        return {
            "status": "erro",
            "detalhe": str(e)
        }

@app.get("/sensores")
async def listar_dados():
    return {
        "dados": dados_sensores,
        "total": len(dados_sensores)
    }

@app.get("/ventoinha")
async def obter_estado_ventoinha():
    return {"estado": ventoinha_estado}

@app.post("/ventoinha")
async def definir_estado_ventoinha(estado: VentoinhaState):
    if estado.estado in ["ligado", "desligado"]:
        set_ventoinha_estado(estado.estado)
        return {"mensagem": f"Ventoinha agora está {ventoinha_estado}"}
    else:
        return {"erro": "Estado inválido! Use 'ligado' ou 'desligado'."}
