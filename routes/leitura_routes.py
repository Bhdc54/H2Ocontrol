from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

# Diretório onde estão os templates HTML
templates = Jinja2Templates(directory="templates")

# Roteador da leitura
router = APIRouter()

@router.get("/leitura", response_class=HTMLResponse)
async def renderizar_grafico(request: Request):
    # Simulação de dados (substitua isso por dados do Firebase ou sensores)
    datas = [datetime(2024, 1, i + 1) for i in range(7)]
    valores = [10, 20, 15, 25, 30, 18, 22]

    # Criação do gráfico com matplotlib
    plt.figure(figsize=(10, 4))
    plt.plot(datas, valores, marker='o', linestyle='-', color='blue')
    plt.title("Leituras do Sensor")
    plt.xlabel("Data")
    plt.ylabel("Valor")
    plt.grid(True)
    plt.tight_layout()

    # Salvar gráfico em memória e codificar para base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    imagem_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Limpar o gráfico atual para evitar sobreposição futura
    plt.clf()

    # Renderizar template com o gráfico
    return templates.TemplateResponse("leitura.html", {
        "request": request,
        "grafico_base64": imagem_base64
    })
