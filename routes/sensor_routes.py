import io
import base64
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
matplotlib.use('Agg') 
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.sensor_models import SensorData, VentoinhaState
from services.ventoinha_service import set_ventoinha_estado, get_ventoinha_estado
from datetime import datetime, timezone, timedelta
from typing import List
from firebase_config import get_firestore_client
from collections import defaultdict

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

@router.get("/grafico", response_class=HTMLResponse)
async def grafico(request: Request, sensor_id: str):
    db = get_firestore_client()
    leituras_ref = db.collection("sensores").document(sensor_id).collection("leituras").stream()

    dados_lista = []
    for doc in leituras_ref:
        dados = doc.to_dict()
        try:
            dt = datetime.strptime(dados["data"], "%d/%m/%Y %H:%M:%S")
            temperatura = float(dados.get("temperatura", 0))
            distancia = float(dados.get("distancia", 0))
            dados_lista.append({"data": dt, "temperatura": temperatura, "distancia": distancia})
        except Exception as e:
            print("Erro ao processar leitura:", e)

    if not dados_lista:
        return HTMLResponse("<h3>Sem dados disponíveis para este sensor.</h3>")

    # Criar DataFrame
    df = pd.DataFrame(dados_lista)

    # Agrupar por dia e pegar máximos e mínimos
    picos = df.groupby(df['data'].dt.date).agg({
        'temperatura': ['max', 'min'],
        'distancia': ['max', 'min']
    }).reset_index()

    # Renomear colunas
    picos.columns = ['data', 'temp_max', 'temp_min', 'dist_max', 'dist_min']

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel("Data")
    ax1.set_ylabel("Temperatura (°C)", color="red")
    ax1.plot(picos['data'], picos['temp_max'], 'r-o', label='Temp Máx')
    ax1.plot(picos['data'], picos['temp_min'], 'r--o', label='Temp Mín')
    ax1.tick_params(axis='y', labelcolor="red")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Distância (cm)", color="blue")
    ax2.plot(picos['data'], picos['dist_max'], 'b-o', label='Dist Máx')
    ax2.plot(picos['data'], picos['dist_min'], 'b--o', label='Dist Mín')
    ax2.tick_params(axis='y', labelcolor="blue")

    plt.title(f"Picos de Temperatura e Distância - {sensor_id}")
    fig.autofmt_xdate()

    # Salvar gráfico em base64 para HTML
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    html = f"""
    <h2>Leituras do Sensor {sensor_id} - Picos Diários</h2>
    <img src='data:image/png;base64,{img_base64}'/>
    """
    return HTMLResponse(html)