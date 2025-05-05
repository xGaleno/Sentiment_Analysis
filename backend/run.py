from dotenv import load_dotenv
from app import create_app
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

# Ejecutar la aplicación si es el archivo principal
if __name__ == '__main__':
    elapsed = time.time() - start_time
    print(f"🚀 Servidor listo para ejecutarse (tiempo de arranque: {elapsed:.2f} segundos)")
    app.run(debug=True)
