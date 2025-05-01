import io
from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_comments_report(comments: list) -> io.BytesIO:
    """
    Genera un informe PDF con resumen automático de comentarios.

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

    # === Generar resumen con modelo BART ===
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(all_text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    except Exception as e:
        summary = "No se pudo generar un resumen automático."
        print("Error al resumir comentarios:", e)

    # === Crear el PDF ===
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Informe de Análisis de Comentarios")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Total de comentarios procesados: {len(comments)}")

    text_object = c.beginText(50, height - 120)
    text_object.setFont("Helvetica", 12)
    text_object.textLines(f"Resumen generado:\n\n{summary}")
    c.drawText(text_object)

    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer
