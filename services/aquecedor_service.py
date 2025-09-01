estado_aquecedor = "desligado"

def set_aquecedor_estado(novo_estado: str):
    global estado_aquecedor
    if novo_estado in ["ligado", "desligado"]:
        estado_aquecedor = novo_estado

def get_aquecedor_estado():
    return estado_aquecedor
