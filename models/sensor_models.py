from pydantic import BaseModel
from typing import Optional

class SensorData(BaseModel):
    temperatura: float
    umidade: float
    distancia: float
    acao_ventoinha: Optional[str] = None
    
class VentoinhaState(BaseModel):
    estado: str  # "ligado" ou "desligado"
    
