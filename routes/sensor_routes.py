from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.sensor_models import SensorData, VentoinhaState
from services.ventoinha_service import set_ventoinha_estado, get_ventoinha_estado
from datetime import datetime
from typing import List
from firebase_config import get_firestore_client
from datetime import datetime, timezone, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

dados_sensores: List[SensorData] = []

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/sensores")
async def receber_dados(data: SensorData):
    try:
        db = get_firestore_client()

        # Fuso horário de Cuiabá (UTC-4)
        fuso_mt = timezone(timedelta(hours=-4))
        agora = datetime.now(fuso_mt)

        db.collection("sensores").document("sensor1").set({
            "temperatura": data.temperatura,
            "distancia": data.distancia,
            "data": agora.strftime("%d/%m/%Y %H:%M:%S")
        }, merge=True)

        return {
            "status": "sucesso",
            "timestamp": agora.isoformat()
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "erro",
            "detalhe": str(e)
        }

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
    if estado.estado in ["ligado", "desligado"]:
        set_ventoinha_estado(estado.estado)
        return {"mensagem": f"Ventoinha agora está {get_ventoinha_estado()}"}
    else:
        return {"erro": "Estado inválido! Use 'ligado' ou 'desligado'."}
