import io
import os
import requests
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzVyGvtw2qOhCzvOAzKvOCVPOC5s09bqY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def get_summary_from_gemini(text: str) -> str:
    headers = { "Content-Type": "application/json" }
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Contexto: Alicia Modas es una tienda de ropa femenina en Mendoza.\n"
                    f"Este es un conjunto de opiniones de clientas sobre su experiencia de compra:\n\n{text}\n\n"
                    f"Genera un resumen ejecutivo en español profesional de máximo 100 palabras."
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

def generate_comments_report(comments: list, filtros: dict = None) -> io.BytesIO:
    all_text = " ".join(
        c.get("respuesta", "") for c in comments if isinstance(c.get("respuesta"), str)
    ).strip()
    if not all_text:
        all_text = "No se proporcionaron comentarios válidos para resumir."
    
    summary = get_summary_from_gemini(all_text)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    # Encabezado
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, y, "📄 Informe de Análisis de Comentarios")
    y -= 25
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Fecha de generación: {fecha_actual}")
    y -= 10
    c.drawString(margin, y, f"Total de comentarios procesados: {len(comments)}")
    y -= 10
    if filtros:
        c.drawString(margin, y, f"Filtros aplicados: {filtros}")
        y -= 15

    # Línea separadora
    y -= 10
    c.line(margin, y, width - margin, y)
    y -= 25

    # Resumen
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Resumen generado por IA:")
    y -= 15
    c.setFont("Helvetica", 11)
    lines = simpleSplit(summary, "Helvetica", 11, width - 2 * margin)
    for line in lines:
        if y < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= 15

    # Línea separadora
    y -= 15
    c.line(margin, y, width - margin, y)
    y -= 25

    # Tabla de detalles
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "📊 Detalle de Comentarios:")
    y -= 20
    c.setFont("Helvetica", 10)

    headers = ["Fecha", "Usuario", "Pregunta", "Respuesta", "Sentimiento", "Polaridad"]
    col_widths = [80, 80, 100, 180, 60, 40]

    c.setFillColorRGB(0.9, 0.9, 0.9)
    for i, header in enumerate(headers):
        c.drawString(margin + sum(col_widths[:i]), y, header)
    y -= 15
    c.setFillColorRGB(0, 0, 0)

    for cmt in comments:
        row = [
            cmt.get("timestamp", "")[:19],
            cmt.get("usuario", "")[:18],
            cmt.get("pregunta", "")[:30],
            cmt.get("respuesta", "")[:60],
            cmt.get("sentimiento", ""),
            str(cmt.get("polaridad", ""))
        ]
        for i, value in enumerate(row):
            c.drawString(margin + sum(col_widths[:i]), y, value)
        y -= 12
        if y < margin:
            c.showPage()
            y = height - margin

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
