from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from routes.sensor_routes import router as sensor_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Incluindo as rotas
app.include_router(sensor_router)
