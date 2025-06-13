import os
import requests
import re

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzVyGvtw2qOhCzvOAzKvOCVPOC5s09bqY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def analyze_sentiment(text: str, question: str) -> str:
    """
    Analiza el sentimiento del comentario en relación con la pregunta recibida.
    Devuelve 'positivo', 'negativo', 'neutro' o 'nulo' si la respuesta no
    tiene sentido o no está relacionada con la pregunta. Las respuestas con
    sentimientos encontrados o negativas con aspectos positivos se clasifican
    como 'neutro'.
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
                    f"{contexto} Se hizo la siguiente pregunta al cliente: '{question}'. "
                    f"El cliente respondió: '{text}'. "
                    "Analiza si la respuesta tiene sentido con la pregunta y "
                    "clasifica el sentimiento como 'positivo', 'negativo' o 'neutro'. "
                    "Si la respuesta combina sentimientos opuestos o es negativa con un aspecto positivo, "
                    "considera el resultado como 'neutro'. "
                    "Si la respuesta no es coherente con la pregunta o carece de sentido, "
                    "responde solo con 'nulo'."
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

            if result in {"mixto", "negativo con aspecto positivo"}:
                result = "neutro"

            if result in {"positivo", "negativo", "neutro"}:
                return result
            else:
                return "nulo"  # Resultado inesperado

        print(f"[ERROR {response.status_code}] {response.reason}")
        return "nulo"

    except requests.RequestException as e:
        print("Excepción en la conexión:", e)
        return "nulo"
