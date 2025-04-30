from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_comments_report(comments):
    """
    Genera un informe PDF basado en los comentarios recibidos.
    """
    # Concatenar todas las respuestas
    all_text = " ".join([c.get("respuesta", "") for c in comments if c.get("respuesta")])

    # Resumir usando Hugging Face
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(all_text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']

    # Crear el PDF en memoria
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Informe de Análisis de Comentarios")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Total de comentarios: {len(comments)}")

    text_object = c.beginText(50, height - 120)
    text_object.setFont("Helvetica", 12)
    text_object.textLines(f"Resumen generado:\n\n{summary}")
    c.drawText(text_object)

    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer  # Retorna el buffer listo para ser enviado
