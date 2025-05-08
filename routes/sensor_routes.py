from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.sensor_models import SensorData, VentoinhaState
from services.ventoinha_service import set_ventoinha_estado, get_ventoinha_estado
from datetime import datetime, timezone, timedelta
from typing import List
from firebase_config import get_firestore_client

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/sensores")
async def receber_dados(data: SensorData):
    try:
        db = get_firestore_client()

        # Fuso horário UTC-4 (Cuiabá)
        fuso_mt = timezone(timedelta(hours=-4))
        agora = datetime.now(fuso_mt)

        # 🔁 Atualiza dados atuais do sensor
        db.collection("sensores").document(data.sensorID).set({
            "temperatura": data.temperatura,
            "distancia": data.distancia,
            "data": agora.strftime("%d/%m/%Y %H:%M:%S")
        }, merge=True)

        # 📌 Salva leitura no histórico
        db.collection("sensores").document(data.sensorID).collection("leituras").add({
            "temperatura": data.temperatura,
            "distancia": data.distancia,
            "data": agora.strftime("%d/%m/%Y %H:%M:%S")
        })

        # 🔍 Busca o aquário vinculado a este sensor
        aquarios_ref = list(db.collection("aquarios").where("sensorID", "==", data.sensorID).stream())
        aquario_doc = aquarios_ref[0] if aquarios_ref else None

        if aquario_doc and aquario_doc.exists:
            aquario_data = aquario_doc.to_dict()
            temp_max = aquario_data.get("tempMaxima")
            temp_min = aquario_data.get("tempMinima")

            # 🚨 Verifica limites de temperatura
            if temp_max is not None and data.temperatura >= temp_max:
                set_ventoinha_estado("ligado")
            elif temp_min is not None and data.temperatura <= temp_min:
                set_ventoinha_estado("desligado")

        return {
            "status": "sucesso",
            "timestamp": agora.isoformat(),
            "estado_ventoinha": get_ventoinha_estado()
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
    db = get_firestore_client()
    sensores_ref = db.collection("sensores").stream()
    sensores = {doc.id: doc.to_dict() for doc in sensores_ref}
    return {"sensores": sensores}

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
