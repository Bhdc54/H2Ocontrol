import io
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
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

@router.get("/grafico", response_class=HTMLResponse)
async def grafico(sensor_id: str):
    try:
        db = get_firestore_client()
        colecao = db.collection("sensores").document(sensor_id).collection("leituras").stream()

        datas, temperaturas, distancias = [], [], []

        for doc in colecao:
            dados = doc.to_dict()
            dt = None

            # Processar data
            try:
                if "timeStamp" in dados and not isinstance(dados["timeStamp"], str):
                    dt = dados["timeStamp"]
                elif "data" in dados:
                    dt = datetime.strptime(dados["data"], "%d/%m/%Y %H:%M:%S")
            except:
                continue

            if dt is None:
                continue

            try:
                temp = float(dados.get("temperatura", 0))
                dist = float(dados.get("distancia", 0))

                # Filtro de outliers
                if -20 <= temp <= 80 and 0 <= dist <= 500:
                    datas.append(dt)
                    temperaturas.append(temp)
                    distancias.append(dist)
            except:
                continue

        if not datas:
            return HTMLResponse("<h3>Sem dados para gerar gráfico</h3>", status_code=404)

        # Ordenar
        datas, temperaturas, distancias = zip(*sorted(zip(datas, temperaturas, distancias)))

        # Criar gráfico com dois eixos Y
        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.set_xlabel("Data")
        ax1.set_ylabel("Temperatura (°C)", color="red")
        ax1.plot(datas, temperaturas, "o-", color="red", label="Temperatura (°C)")
        ax1.tick_params(axis="y", labelcolor="red")

        ax2 = ax1.twinx()
        ax2.set_ylabel("Distância (cm)", color="blue")
        ax2.plot(datas, distancias, "x-", color="blue", label="Distância (cm)")
        ax2.tick_params(axis="y", labelcolor="blue")

        # Formatar eixo X
        import matplotlib.dates as mdates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
        fig.autofmt_xdate()

        plt.title(f"Leituras do Sensor {sensor_id}")
        fig.tight_layout()

        # Converter para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

        html_content = f"""
        <html>
        <head><title>Gráfico do Sensor</title></head>
        <body>
            <h2>Leituras do Sensor {sensor_id}</h2>
            <img src="data:image/png;base64,{img_base64}"/>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"Erro ao gerar gráfico: {e}", status_code=500)
