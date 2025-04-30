from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa o Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# Configuração dos templates HTML
templates = Jinja2Templates(directory="templates")

# Modelo de dados recebido do sensor
class SensorData(BaseModel):
    temperatura: float
    umidade: float
    distancia: float
    acao_ventoinha: Optional[str] = None

# Modelo para alterar o estado da ventoinha
class VentoinhaState(BaseModel):
    estado: str  # "ligado" ou "desligado"

# Lista para armazenar os dados localmente (opcional)
dados_sensores: List[SensorData] = []

# Estado da ventoinha
ventoinha_estado = "desligado"

# Função para definir o estado da ventoinha
def set_ventoinha_estado(novo_estado: str):
    global ventoinha_estado
    if novo_estado in ["ligado", "desligado"]:
        ventoinha_estado = novo_estado
        print(f"✅ Ventoinha agora está {ventoinha_estado}")
    else:
        print(f"❌ Estado inválido recebido: {novo_estado}")

# Página principal (HTML)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota para receber dados do sensor (POST)
@app.post("/sensores")
async def receber_dados(data: SensorData):
    try:
        dados_sensores.append(data)

        print(f"📡 Dados recebidos - Temperatura: {data.temperatura}, Umidade: {data.umidade}, Distância: {data.distancia}")

        # Atualiza estado da ventoinha conforme ação recebida
        if data.acao_ventoinha == "ligar":
            set_ventoinha_estado("ligado")
        elif data.acao_ventoinha == "desligar":
            set_ventoinha_estado("desligado")

        # Salva no Firestore: sensores/sensor1/leituras/<doc>
        sensor_doc_ref = db.collection("sensores").document("sensor1").collection("leituras").document()
        sensor_doc_ref.set({
            "temperatura": data.temperatura,
            "umidade": data.umidade,
            "distancia": data.distancia,
            "status": True,
            "usuario": "J8hN95ukOCxYTdMeoACxwtr9FjN2",  # ID do usuário
            "aquarioID": "eHTUh0DKSeCp83rupL1G",         # ID do aquário
            "timeStamp": datetime.now().strftime("%d de %B de %Y às %H:%M:%S UTC-4"),
            "acao_ventoinha": data.acao_ventoinha,
            "estado_ventoinha": ventoinha_estado
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

# Rota para listar dados locais
@app.get("/sensores")
async def listar_dados():
    return {
        "dados": dados_sensores,
        "total": len(dados_sensores)
    }

# Rota para obter o estado da ventoinha
@app.get("/ventoinha")
async def obter_estado_ventoinha():
    return {"estado": ventoinha_estado}

# Rota para alterar manualmente o estado da ventoinha
@app.post("/ventoinha")
async def definir_estado_ventoinha(estado: VentoinhaState):
    if estado.estado in ["ligado", "desligado"]:
        set_ventoinha_estado(estado.estado)
        return {"mensagem": f"Ventoinha agora está {ventoinha_estado}"}
    else:
        return {"erro": "Estado inválido! Use 'ligado' ou 'desligado'."}
