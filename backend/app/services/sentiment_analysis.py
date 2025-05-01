import os
import requests

# Cargar clave de API desde entorno
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD6e8l8vNIvp_8dgNyeG5DGCTyF-xHYUK0")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def analyze_sentiment(text: str) -> str:
    """
    Realiza análisis de sentimiento sobre un comentario usando Gemini API.

    Args:
        text (str): Comentario del usuario.

    Returns:
        str: 'positivo', 'negativo', 'neutro' o 'Error'
    """
    headers = { "Content-Type": "application/json" }
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Analiza el sentimiento del siguiente comentario y responde solo con una palabra (positivo, negativo o neutro): '{text}'"
            }]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            result = data.get('candidates', [])[0]['content']['parts'][0]['text'].strip().lower()

            if "positivo" in result:
                return "positivo"
            elif "negativo" in result:
                return "negativo"
            else:
                return "neutro"
        
        print(f"[ERROR {response.status_code}] {response.reason}")
        print(response.text)
        return "Error"

    except requests.RequestException as e:
        print("Excepción en la conexión:", e)
        return "Error"
