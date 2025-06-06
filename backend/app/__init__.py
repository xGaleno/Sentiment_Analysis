from flask import Flask
from flask_cors import CORS
from .routes import register_routes

def create_app():
    """Inicializa la aplicación Flask con CORS y rutas registradas."""
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    register_routes(app)
    return app
