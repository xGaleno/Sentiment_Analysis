from flask import Flask
from flask_cors import CORS
from .routes import register_routes

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    CORS(app, supports_credentials=True)
    register_routes(app)
    return app
