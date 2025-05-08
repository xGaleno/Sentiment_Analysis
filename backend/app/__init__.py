import os
from flask import Flask
from flask_cors import CORS
from .routes import register_routes

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))  # backend/app
    templates_path = os.path.join(base_dir, 'templates')   # backend/app/templates

    app = Flask(__name__, template_folder=templates_path)
    CORS(app, supports_credentials=True)
    register_routes(app)
    return app
