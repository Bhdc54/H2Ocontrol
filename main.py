from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from routes.sensor_routes import router as sensor_router
from routes.notificacao_routes import router as notificacao_router  # ✅ Nova rota

# Inicializa o Firebase
try:
    import firebase_config
    print("✅ Firebase inicializado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao inicializar Firebase: {str(e)}")
    raise

app = FastAPI(
    title="H2O Control API",
    description="API para monitoramento de sensores",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

# Rotas
app.include_router(sensor_router)
app.include_router(notificacao_router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "firebase": "connected"}
