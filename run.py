import os
import time
from dotenv import load_dotenv
from backend import create_app

print("🔧 Iniciando carga del servidor...")

start_time = time.time()
load_dotenv()
print("✅ Variables de entorno cargadas")

app = create_app()
print("✅ Aplicación Flask creada")

elapsed = time.time() - start_time
print(f"🚀 Aplicación inicializada en {elapsed:.2f} segundos")
