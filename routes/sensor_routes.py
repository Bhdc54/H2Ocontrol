import io
import base64
import matplotlib.pyplot as plt
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

        fuso_mt = timezone(timedelta(hours=-4))
        agora = datetime.now(fuso_mt)

        # Atualiza dados atuais do sensor
        db.collection("sensores").document(data.sensorID).set({
            "temperatura": data.temperatura,
            "distancia": data.distancia,
            "data": agora.strftime("%d/%m/%Y %H:%M:%S")
        }, merge=True)

        # Salva leitura no histórico
        db.collection("sensores").document(data.sensorID).collection("leituras").add({
            "sensorID": data.sensorID,
            "temperatura": data.temperatura,
            "distancia": data.distancia,
            "data": agora.strftime("%d/%m/%Y %H:%M:%S")
        })

        # Verifica limites de temperatura
        aquarios_ref = list(db.collection("aquarios").where("sensorID", "==", data.sensorID).stream())
        aquario_doc = aquarios_ref[0] if aquarios_ref else None

        if aquario_doc and aquario_doc.exists:
            aquario_data = aquario_doc.to_dict()
            temp_max = aquario_data.get("tempMaxima")
            temp_min = aquario_data.get("tempMinima")

            estado_atual = get_ventoinha_estado()

            if temp_max is not None:
                if data.temperatura >= temp_max and estado_atual == "desligado":
                    set_ventoinha_estado("ligado")
                elif data.temperatura < temp_max - 1 and estado_atual == "ligado":
                    set_ventoinha_estado("desligado")

        return {
            "status": "sucesso",
            "timestamp": agora.isoformat(),
            "estado_ventoinha": get_ventoinha_estado()
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "erro", "detalhe": str(e)}

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

# NOVA ROTA PARA GRÁFICO
@router.get("/grafico", response_class=HTMLResponse)
async def grafico(request: Request, sensor_id: str):
    db = get_firestore_client()
    leituras_ref = db.collection("sensores").document(sensor_id).collection("leituras").stream()

    dados_lista = []
    for doc in leituras_ref:
        dados = doc.to_dict()
        try:
            dt = datetime.strptime(dados["data"], "%d/%m/%Y %H:%M:%S")
            dados_lista.append({
                "data": dt,
                "temperatura": dados.get("temperatura", 0),
                "distancia": dados.get("distancia", 0)
            })
        except:
            continue

    # Ordena pelo datetime
    dados_lista.sort(key=lambda x: x["data"])

    if not dados_lista:
        return HTMLResponse(content="<h3>Sem dados para este sensor.</h3>", status_code=200)

    datas = [item["data"] for item in dados_lista]
    temperaturas = [item["temperatura"] for item in dados_lista]
    distancias = [item["distancia"] for item in dados_lista]

    plt.figure(figsize=(10, 5))
    plt.plot(datas, temperaturas, label="Temperatura (°C)", color="red", marker="o")
    plt.plot(datas, distancias, label="Distância (cm)", color="blue", marker="x")
    plt.xlabel("Data")
    plt.ylabel("Valores")
    plt.title(f"Histórico do Sensor {sensor_id}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    return templates.TemplateResponse("grafico.html", {
        "request": request,
        "sensor_id": sensor_id,
        "grafico": img_base64
    })