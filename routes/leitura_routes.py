from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase_config import get_firestore_client

import matplotlib.pyplot as plt
import pandas as pd
import base64
import io

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/leitura", response_class=HTMLResponse)
async def exibir_leitura(request: Request):
    try:
        db = get_firestore_client()

        sensores_ref = db.collection("sensores").stream()
        sensores = [doc.id for doc in sensores_ref]

        dados = []

        for sensor_id in sensores:
            leituras_ref = db.collection("sensores").document(sensor_id).collection("leituras").stream()
            for leitura in leituras_ref:
                item = leitura.to_dict()
                dados.append({
                    "sensorID": sensor_id,
                    "temperatura": item.get("temperatura"),
                    "distancia": item.get("distancia"),
                    "data": item.get("data")
                })

        df = pd.DataFrame(dados)

        if df.empty:
           # Estatísticas
            temp_media = df["temperatura"].mean()
            temp_min = df["temperatura"].min()
            temp_max = df["temperatura"].max()

            dist_media = df["distancia"].mean()
            dist_min = df["distancia"].min()
            dist_max = df["distancia"].max()

            return templates.TemplateResponse("leitura.html", {
                "request": request,
                "grafico_base64": grafico_base64,
                "temp_media": round(temp_media, 2),
                "temp_min": temp_min,
                "temp_max": temp_max,
                "dist_media": round(dist_media, 2),
                "dist_min": dist_min,
                "dist_max": dist_max
})

        try:
            df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y %H:%M:%S")
            df.sort_values("data", inplace=True)
        except:
            pass

        plt.figure(figsize=(10, 4))
        plt.plot(df["temperatura"], label="Temperatura (°C)", color="red")
        plt.plot(df["distancia"], label="Distância (cm)", color="blue")
        plt.title("Gráfico de Leituras")
        plt.xlabel("Amostras")
        plt.ylabel("Valores")
        plt.legend()
        plt.grid(True)

        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()
        buffer.seek(0)

        grafico_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return templates.TemplateResponse("leitura.html", {
            "request": request,
            "grafico_base64": grafico_base64
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("leitura.html", {
            "request": request,
            "grafico_base64": "",
            "mensagem": f"Erro: {str(e)}"
        })
