import os
from dotenv import load_dotenv

load_dotenv()  # ✅ Carga variables desde .env

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
