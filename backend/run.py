from dotenv import load_dotenv
from app import create_app
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Crear instancia de la aplicación Flask
app = create_app()

# Ejecutar la aplicación si es el archivo principal
if __name__ == '__main__':
    app.run(debug=True)
