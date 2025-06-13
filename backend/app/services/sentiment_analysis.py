import os
import requests
import re

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzVyGvtw2qOhCzvOAzKvOCVPOC5s09bqY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def analyze_sentiment(text: str) -> str:
    """
    Analiza el sentimiento del comentario. Devuelve:
    - 'positivo'
    - 'negativo'
    - 'neutro' si hay mezcla clara de sentimientos
    - 'nulo' si la respuesta no tiene sentido con la pregunta
    """
    headers = {"Content-Type": "application/json"}
    contexto = (
        "Contexto: La empresa Alicia Modas es una PYME familiar ubicada en Mendoza, Argentina, "
        "dedicada a la venta de indumentaria femenina y accesorios de moda. Ofrece productos de "
        "fabricación propia y nacionales, destacándose por su atención personalizada y fuerte presencia en redes sociales."
    )

    prompt = (
        f"{contexto}\n"
        f"Analiza el siguiente comentario del cliente y responde con una sola palabra entre las siguientes opciones:\n"
        f"- positivo: si expresa satisfacción clara\n"
        f"- negativo: si expresa una queja o disconformidad\n"
        f"- neutro: si hay una mezcla de emociones positivas y negativas\n"
        f"- nulo: si el comentario no tiene sentido o no está relacionado con la experiencia del cliente\n\n"
        f"Comentario: \"{text}\"\n"
        f"Respuesta:"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
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

            if result in {"positivo", "negativo", "neutro"}:
                # Verificación adicional de validez semántica para evitar que "hola" sea considerado neutro
                palabras_validas = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]{3,}\b', text)
                if len(palabras_validas) < 3:  # requiere al menos 3 palabras sustanciales
                    return "nulo"
                return result

            return "nulo"

        print(f"[ERROR {response.status_code}] {response.reason}")
        return "nulo"

    except requests.RequestException as e:
        print("Excepción en la conexión:", e)
        return "nulo"
