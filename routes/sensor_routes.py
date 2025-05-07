from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.sensor_models import SensorData, VentoinhaState
from services.ventoinha_service import set_ventoinha_estado, get_ventoinha_estado
from datetime import datetime
from typing import List
from firebase_config import get_firestore_client

router = APIRouter()
templates = Jinja2Templates(directory="templates")
db = get_firestore_client()  # Conexão com o Firebase

dados_sensores: List[SensorData] = []

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/sensores")
async def receber_dados(data: SensorData):
    try:
        dados_sensores.append(data)

        print(f"📡 Dados recebidos - Temperatura: {data.temperatura}, Distância: {data.distancia}")

        # Se houver ação na ventoinha, atualize o estado
        if data.acao_ventoinha == "ligar":
            set_ventoinha_estado("ligado")
        elif data.acao_ventoinha == "desligar":
            set_ventoinha_estado("desligado")

        # Salva no Firebase
        db.collection("sensores").document("sensor1").collection("leituras").add({
            "temperatura": data.temperatura,
            "nivelAgua": data.distancia,
            "status": data.status,
            "timeStamp": datetime.now().strftime("%d de %B de %Y às %H:%M:%S UTC-4"),
            "usuario": data.usuario,
            "aquarioID": data.aquarioID
        })

        return {
            "status": "sucesso",
            "timestamp": datetime.now().isoformat(),
            "ventoinha_estado_atual": get_ventoinha_estado()
        }

    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}

@router.get("/sensores")
async def listar_dados():
    return {
        "dados": dados_sensores,
        "total": len(dados_sensores)
    }

@router.get("/ventoinha")
async def obter_estado_ventoinha():
    return {"estado": get_ventoinha_estado()}

@router.post("/ventoinha")
async def definir_estado_ventoinha(estado: VentoinhaState):
    try:
        # Valida e atualiza o estado
        if estado.estado in ["ligado", "desligado"]:
            set_ventoinha_estado(estado.estado)
            
            # Salva no Firebase (coleção separada para histórico)
            db.collection("ventoinha_estados").add({
                "estado": estado.estado,
                "timestamp": datetime.now(),
                "usuario": estado.usuario if estado.usuario else "Sistema",
                "aquarioID": estado.aquarioID if estado.aquarioID else "default"
            })
            
            return {"mensagem": f"Ventoinha agora está {estado.estado}"}
        else:
            return {"erro": "Estado inválido! Use 'ligado' ou 'desligado'."}
    
    except Exception as e:
        return {"erro": str(e)}