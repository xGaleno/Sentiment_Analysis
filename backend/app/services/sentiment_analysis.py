import os
import requests
import re

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAeqdJSv2fxlM18pBzG-AKLVgpKTyoco3A")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def analyze_sentiment(text: str) -> str:
    """
    Analiza el sentimiento del comentario. Devuelve 'positivo', 'negativo', 'neutro' o 'nulo' si no tiene sentido.
    """
    headers = { "Content-Type": "application/json" }
    contexto = (
        "Contexto: La empresa Alicia Modas es una PYME familiar ubicada en Mendoza, Argentina, "
        "dedicada a la venta de indumentaria femenina y accesorios de moda. Ofrece productos de "
        "fabricación propia y nacionales, destacándose por su atención personalizada y fuerte presencia en redes sociales."
    )

    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"{contexto} Analiza el sentimiento del siguiente comentario del cliente "
                    f"y responde solo con una palabra (positivo, negativo o neutro): '{text}'"
                )
            }]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            try:
                result = data.get('candidates', [])[0]['content']['parts'][0]['text'].strip().lower()
            except (IndexError, KeyError, AttributeError):
                return "nulo"

            # Si el resultado es 'neutro', evaluamos si el texto tiene sentido
            if result == "neutro":
                palabras_validas = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]{3,}\b', text)
                if len(palabras_validas) == 0:
                    return "nulo"

            if result in {"positivo", "negativo", "neutro"}:
                return result
            else:
                return "nulo"  # Resultado inesperado

        print(f"[ERROR {response.status_code}] {response.reason}")
        return "nulo"

    except requests.RequestException as e:
        print("Excepción en la conexión:", e)
        return "nulo"