ventoinha_estado = "desligado"

def set_ventoinha_estado(novo_estado: str):
    global ventoinha_estado
    if novo_estado in ["ligado", "desligado"]:
        ventoinha_estado = novo_estado
        print(f"✅ Ventoinha agora está {ventoinha_estado}")
    else:
        print(f"❌ Estado inválido recebido: {novo_estado}")

def get_ventoinha_estado():
    return ventoinha_estado
