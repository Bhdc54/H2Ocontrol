from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import firestore
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/leituras", response_class=HTMLResponse)
async def exibir_leituras(request: Request):
    db = firestore.client()
    leituras_ref = db.collection("leituras")
    docs = leituras_ref.stream()

    dados = []
    for doc in docs:
        leitura = doc.to_dict()
        leitura["id"] = doc.id
        dados.append(leitura)

    df = pd.DataFrame(dados)

    if not df.empty:
        # Convertendo timestamps, se necessário
        if 'timestamp' in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
            df = df.sort_values("timestamp")

        # Cálculo de estatísticas
        temp_media = df["temperatura"].mean()
        temp_max = df["temperatura"].max()
        temp_min = df["temperatura"].min()

        umid_media = df["umidade"].mean()
        umid_max = df["umidade"].max()
        umid_min = df["umidade"].min()

        # Geração do gráfico
        plt.figure(figsize=(10, 5))
        plt.plot(df["timestamp"], df["temperatura"], label="Temperatura (°C)", color="red", marker='o')
        plt.plot(df["timestamp"], df["umidade"], label="Umidade (%)", color="blue", marker='x')
        plt.xlabel("Data e Hora")
        plt.ylabel("Valores")
        plt.title("Temperatura e Umidade ao longo do tempo")
        plt.legend()
        plt.grid(True)

        # Converter o gráfico para base64
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()

        return templates.TemplateResponse("leitura.html", {
            "request": request,
            "grafico_base64": image_base64,
            "temp_media": f"{temp_media:.2f}",
            "temp_max": f"{temp_max:.2f}",
            "temp_min": f"{temp_min:.2f}",
            "umid_media": f"{umid_media:.2f}",
            "umid_max": f"{umid_max:.2f}",
            "umid_min": f"{umid_min:.2f}"
        })

    else:
        return templates.TemplateResponse("leitura.html", {
            "request": request,
            "grafico_base64": "",
            "mensagem": "Sem dados disponíveis."
        })
