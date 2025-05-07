from pydantic import BaseModel
from typing import Optional

class SensorData(BaseModel):
    temperatura: float
    umidade: float
    distancia: float
    status: bool  # ✅ Adicione esta linha
    acao_ventoinha: Optional[str] = None
    usuario: Optional[str] = None
    aquarioID: Optional[str] = None
