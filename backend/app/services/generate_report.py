import io
import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzVyGvtw2qOhCzvOAzKvOCVPOC5s09bqY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def get_summary_from_gemini(text: str) -> str:
    """
    Envía texto a Gemini API para generar un resumen breve.
    """
    headers = { "Content-Type": "application/json" }
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Contexto: Alicia Modas es una tienda de ropa femenina y accesorios en Mendoza. "
                    f"Este es un conjunto de opiniones de clientas sobre su experiencia de compra:\n\n{text}\n\n"
                    f"Genera un resumen en lenguaje natural claro y profesional de no más de 100 palabras."
                )
            }]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get('candidates', [])[0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print("❌ Error al obtener resumen de Gemini:", e)
        return "No se pudo generar un resumen automático."

def generate_comments_report(comments: list) -> io.BytesIO:
    """
    Genera un informe PDF con resumen automático de comentarios usando Gemini API.

    Args:
        comments (list): Lista de diccionarios con comentarios (espera clave 'respuesta').

    Returns:
        BytesIO: Archivo PDF generado en memoria listo para descarga o envío.
    """
    # === Consolidar texto para resumen ===
    all_text = " ".join(
        c.get("respuesta", "") for c in comments if isinstance(c.get("respuesta"), str)
    ).strip()

    if not all_text:
        all_text = "No se proporcionaron comentarios válidos para resumir."

    summary = get_summary_from_gemini(all_text)

    # === Crear el PDF ===
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Informe de Análisis de Comentarios")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Total de comentarios procesados: {len(comments)}")

    c.setFont("Helvetica", 12)
    text_lines = simpleSplit(f"Resumen generado:\n\n{summary}", "Helvetica", 12, maxWidth=width - 100)
    
    text_object = c.beginText(50, height - 120)
    for line in text_lines:
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)


    return buffer
