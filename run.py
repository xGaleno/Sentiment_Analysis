from dotenv import load_dotenv
from backend.app import create_app
import os
import time

print("🔧 Iniciando carga del servidor...")

# Medir tiempo de arranque
start_time = time.time()

# Cargar variables de entorno desde .env
load_dotenv()
print("✅ Variables de entorno cargadas")

# Crear instancia de la aplicación Flask
app = create_app()
print("✅ Aplicación Flask creada")

# Mostrar tiempo de arranque
elapsed = time.time() - start_time
print(f"🚀 Aplicación inicializada en {elapsed:.2f} segundos")

# No colocar app.run() aquí en producción.
# Gunicorn o Waitress deben usar: `run:app`