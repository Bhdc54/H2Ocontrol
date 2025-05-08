from pydantic import BaseModel
from typing import Optional

class SensorData(BaseModel):
    sensorID: str
    temperatura: float
    distancia: float
    
    
class VentoinhaState(BaseModel):
    estado: str  # "ligado" ou "desligado"
    
