import os
import requests
import re

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzVyGvtw2qOhCzvOAzKvOCVPOC5s09bqY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

# Fallback basado en respuestas típicas del cliente
RESPUESTAS_COMUNES = {
    "ok": "neutro",
    "bien": "positivo",
    "muy bien": "positivo",
    "excelente": "positivo",
    "todo bien": "positivo",
    "normal": "neutro",
    "más o menos": "neutro",
    "regular": "neutro",
    "meh": "neutro",
    "la atención": "negativo",
    "mal": "negativo",
    "pésimo": "negativo",
    "horrible": "negativo",
    "nada": "negativo",
    "no sé": "nulo",
    "ns/nr": "nulo",
}

def interpretar_directo(respuesta: str) -> str:
    """Evalúa respuestas breves sin llamar al modelo."""
    r = respuesta.strip().lower()
    return RESPUESTAS_COMUNES.get(r, None)

def analyze_sentiment(question: str, answer: str) -> str:
    """
    Analiza el sentimiento de una respuesta dada una pregunta.
    Devuelve:
    - 'positivo'
    - 'negativo'
    - 'neutro'
    - 'nulo'
    """
    # Verificación directa si la respuesta es una frase corta conocida
    directo = interpretar_directo(answer)
    if directo:
        return directo

    headers = {"Content-Type": "application/json"}
    contexto = (
        "Contexto: Alicia Modas es una tienda de ropa femenina con buena atención y productos propios. "
        "Queremos evaluar si los comentarios reflejan satisfacción, quejas o neutralidad."
    )

    prompt = (
        f"{contexto}\n"
        f"Clasifica el siguiente comentario SOLO con una palabra:\n"
        f"- positivo\n- negativo\n- neutro\n- nulo (si no tiene sentido o no responde a la pregunta)\n\n"
        f"Pregunta: \"{question}\"\n"
        f"Comentario del cliente: \"{answer}\"\n"
        f"Clasificación:"
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
            result_text = data.get('candidates', [])[0]['content']['parts'][0]['text'].strip().lower()

            # Extraer la primera palabra válida
            match = re.match(r"\b(positivo|negativo|neutro|nulo)\b", result_text)
            if match:
                return match.group(1)

            # Si responde con una oración, intentamos encontrar la palabra clave
            for palabra in ["positivo", "negativo", "neutro", "nulo"]:
                if palabra in result_text:
                    return palabra

            return "nulo"  # Si todo falla

        print(f"[ERROR {response.status_code}] {response.reason}")
        return "nulo"

    except requests.RequestException as e:
        print("Excepción en la conexión:", e)
        return "nulo"