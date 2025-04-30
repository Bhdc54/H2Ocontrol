from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI()

# Configuração do template
templates = Jinja2Templates(directory="templates")
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelo de dados do sensor
class SensorData(BaseModel):
    temperatura: float
    umidade: float
    distancia: float
    acao_ventoinha: Optional[str] = None

# Modelo para controle da ventoinha
class VentoinhaState(BaseModel):
    estado: str  # "ligado" ou "desligado"

# Lista de dados do sensor
dados_sensores: List[SensorData] = []

# Estado atual da ventoinha
ventoinha_estado = "desligado"

# Função para alterar estado da ventoinha
def set_ventoinha_estado(novo_estado: str):
    global ventoinha_estado
    if novo_estado in ["ligado", "desligado"]:
        ventoinha_estado = novo_estado
        print(f"✅ Ventoinha agora está {ventoinha_estado}")
    else:
        print(f"❌ Estado inválido recebido: {novo_estado}")

# Página principal com HTML
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota para receber dados do Arduino
@app.post("/sensores")
async def receber_dados(data: SensorData):
    try:
        dados_sensores.append(data)

        print(f"📡 Dados recebidos - Temperatura: {data.temperatura}, Umidade: {data.umidade}, Distância: {data.distancia}")

        if data.acao_ventoinha == "ligar":
            set_ventoinha_estado("ligado")
        elif data.acao_ventoinha == "desligar":
            set_ventoinha_estado("desligado")

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

# Rota para listar dados
@app.get("/sensores")
async def listar_dados():
    return {
        "dados": dados_sensores,
        "total": len(dados_sensores)
    }

# Rota para consultar estado da ventoinha
@app.get("/ventoinha")
async def obter_estado_ventoinha():
    return {"estado": ventoinha_estado}

# Rota para alterar estado da ventoinha manualmente
@app.post("/ventoinha")
async def definir_estado_ventoinha(estado: VentoinhaState):
    if estado.estado in ["ligado", "desligado"]:
        set_ventoinha_estado(estado.estado)
        return {"mensagem": f"Ventoinha agora está {ventoinha_estado}"}
    else:
        return {"erro": "Estado inválido! Use 'ligado' ou 'desligado'."}