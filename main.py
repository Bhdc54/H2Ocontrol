from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from routes.sensor_routes import router as sensor_router
from routes import leitura_routes

# Inicializa o Firebase antes de criar o app FastAPI
try:
    import firebase_config
    print("Firebase inicializado com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar Firebase: {str(e)}")
    raise

# Cria a aplicação FastAPI
app = FastAPI(
    title="H2O Control API",
    description="API para monitoramento de sensores",
    version="1.0.0"
)

# Configura templates Jinja2
templates = Jinja2Templates(directory="templates")

# Inclui as rotas com prefixo e tags para documentação
app.include_router(sensor_router)
app.include_router(leitura_routes)

# Adiciona rota de health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "firebase": "connected"}

