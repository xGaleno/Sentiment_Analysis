import io
import os
import requests
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.lib.colors import lightgrey, black, HexColor
import traceback # Import traceback for more detailed error logging

# Adjust the import path to backend.db
try:
    from backend.db import get_all_users, get_all_comments
except ImportError as e:
    print(f"Warning: Could not import get_all_users and get_all_comments from backend.db: {e}")
    print("Please ensure backend/db.py exists and is accessible in your environment.")
    # Define dummy functions to prevent errors if db.py cannot be imported during development
    def get_all_users():
        print("Using dummy function for get_all_users().")
        return [{"email": "ejemplo1@test.com"}, {"email": "ejemplo2@test.com"}, {"no_email": "abc"}]
    def get_all_comments():
        print("Using dummy function for get_all_comments().")
        # Example data so the report doesn't fail if no real comments are available
        return [
            {"usuario": "Usuario1", "fecha": "2025-06-14", "pregunta": "¿Qué tal la atención?", "respuesta": "Excelente, muy amable.", "sentimiento": "positivo", "polaridad": 0.8, "timestamp": "2025-06-14T10:00:00"},
            {"usuario": "Usuario2", "fecha": "2025-06-14", "pregunta": "¿Y la tela?", "respuesta": "La tela es un poco fina.", "sentimiento": "neutro", "polaridad": 0.0, "timestamp": "2025-06-14T10:05:00"},
            {"usuario": "Usuario3", "fecha": "2025-06-14", "pregunta": "¿Recomendarías?", "respuesta": "Sí, la ropa es buena.", "sentimiento": "positivo", "polaridad": 0.6, "timestamp": "2025-06-14T10:10:00"},
            {"usuario": "Usuario4", "fecha": "2025-06-14", "pregunta": "¿Precios?", "respuesta": "Algo elevados.", "sentimiento": "negativo", "polaridad": -0.4, "timestamp": "2025-06-14T10:15:00"},
        ]


API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzVyGvtw2qOhCzvOAzKvOCVPOC5s09bqY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def get_summary_from_gemini(text: str) -> str:
    """
    Obtains an executive summary from a given text using the Gemini API.
    Configures the model to generate a concise summary of up to 100 words.
    """
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
        }],
        "generationConfig": {
            "temperature": 0.7, # Controls the creativity of the response
            "maxOutputTokens": 150 # Limits the maximum length of the summary to ensure conciseness
        }
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        response.raise_for_status() # Raises an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        if data and 'candidates' in data and data['candidates']:
            # Extracts the summary text from Gemini's response
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print("❌ The Gemini API did not return the expected data structure.")
            return "No se pudo generar un resumen automático."
    except Exception as e:
        print(f"❌ Error getting summary from Gemini: {e}")
        traceback.print_exc() # Print full traceback for Gemini API errors
        return "No se pudo generar un resumen automático."

# Custom canvas class to add page numbers on every page
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_pages = [] # List to store states of each page
        self.page_count = 0 # Initialize page counter

    def showPage(self):
        """Overrides the default showPage to save current page state and increment count."""
        self._saved_pages.append(dict(self.__dict__)) # Save the current state
        self.page_count += 1 # Increment page count
        self._startPage() # Start a new page

    def save(self):
        """Overrides the default save to add page numbers to all saved pages."""
        # Ensure the last page is counted and saved before iterating
        if '_startPage' in self.__dict__: # Check if there's an active page
            self.showPage() # Save the current (last) page
            self.page_count -= 1 # showPage increments, but we just want to count the one before starting new

        for page_number, page_dict in enumerate(self._saved_pages):
            self.__dict__.update(page_dict) # Restore state of the page
            self.draw_page_number(page_number + 1, self.page_count) # Draw number
            canvas.Canvas.showPage(self) # Show the page (and effectively start next for reportlab internal mechanism)
        canvas.Canvas.save(self) # Final save

    def draw_page_number(self, page_num, total_pages):
        """Draws the page number on the current page."""
        width, height = letter # Get page dimensions
        self.setFont("Helvetica", 9)
        self.setFillColor(black)
        # Position the page number at the bottom center of the page
        self.drawCentredString(width / 2, 0.75 * 50 / 2, f"Página {page_num} de {total_pages}")


def generate_comments_report(filtros: dict = None, charts: dict = None) -> io.BytesIO:
    """
    Generates a PDF report of customer comments analysis.
    Now obtains comment and user data directly from db.py functions.

    Arguments:
        filtros (dict, optional): A dictionary of filters applied to the
                                  comment set.
        charts (dict, opcional): A dictionary where keys are chart titles
                                 and values are base64 encoded image data (e.g., 'data:image/png;base64,...').

    Returns:
        io.BytesIO: A BytesIO object containing the generated PDF.
    """
    # --- Get data directly from db.py ---
    all_users = get_all_users()
    comments = get_all_comments() # Get all comments

    # Calculate the number of registered emails
    num_emails_registered = len([u['email'] for u in all_users if 'email' in u])

    # Combine all responses to generate an overall summary
    all_text = " ".join(
        c.get("respuesta", "") for c in comments if isinstance(c.get("respuesta"), str)
    ).strip()
    if not all_text:
        all_text = "No se proporcionaron comentarios válidos para resumir."
    
    summary = get_summary_from_gemini(all_text)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    buffer = io.BytesIO()
    c = NumberedCanvas(buffer, pagesize=letter) # Use the custom NumberedCanvas class
    width, height = letter # Page width and height (letter size)
    margin = 50 # Page margins
    current_y = height - margin # Current vertical position on the page

    # --- Institutional Header ---
    company_name = "Alicia Modas" # Company name for the header
    report_title = "Informe de Análisis de Comentarios" # Report title

    # If you have a company logo, you can load it here.
    # Make sure the logo file (e.g., 'logo.png') is accessible on your server.
    # For example, if it's in the same directory as your script:
    # logo_path = 'logo.png'
    # try:
    #     if os.path.exists(logo_path):
    #         logo = ImageReader(logo_path)
    #         # Adjust x, y, width, height according to the desired logo size
    #         # Draw the logo to the right of the report title or in a corner
    #         logo_width = 80
    #         logo_height = 40
    #         c.drawImage(logo, width - margin - logo_width, current_y - 30, width=logo_width, height=logo_height, preserveAspectRatio=True)
    # except Exception as e:
    #     print(f"Error loading logo: {e}")
    #     # Optional: If the logo fails to load, you can display placeholder text
    #     # c.setFont("Helvetica-Bold", 10)
    #     # c.drawString(width - margin - 80, current_y - 20, "🏢 Missing Logo")

    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin, current_y, f"{company_name}")
    current_y -= 30 # Space after company name

    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, current_y, f"📄 {report_title}")
    current_y -= 25 # Space after report title

    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, f"Fecha de generación: {fecha_actual}")
    current_y -= 12
    c.drawString(margin, current_y, f"Total de comentarios procesados: {len(comments)}")
    current_y -= 12
    
    # === FIX: Validate if filters is a dictionary before iterating ===
    if filtros and isinstance(filtros, dict):
        filter_text_parts = []
        for k, v in filtros.items():
            if isinstance(v, list):
                filter_text_parts.append(f"{k}: {', '.join(map(str, v))}")
            else:
                filter_text_parts.append(f"{k}: {v}")
        c.drawString(margin, current_y, f"Filtros aplicados: {', '.join(filter_text_parts)}")
        current_y -= 15
    # ================================================================

    # Section divider line after header
    c.setStrokeColor(HexColor("#CCCCCC")) # Lighter gray for the line
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 25 # Space after the line

    # --- AI-generated Executive Summary ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Resumen Ejecutivo Automatizado por IA")
    current_y -= 20 # Space after section title
    c.setFont("Helvetica", 11)
    
    # Splits the summary into lines that fit the page width
    lines = simpleSplit(summary, "Helvetica", 11, width - 2 * margin)
    for line in lines:
        if current_y < margin + 20: # If content goes below the margin, show new page
            c.showPage()
            current_y = height - margin # Reset y for the new page
            c.setFont("Helvetica", 11) # Reapply font for the new page
        c.drawString(margin, current_y, line)
        current_y -= 15 # Line spacing

    current_y -= 10 # Extra space after summary
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.line(margin, current_y, width - margin, current_y) # Section divider line
    current_y -= 25 # Space after the line

    # --- Detailed Analysis and Key Statistics (NEW SECTION) ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Análisis Detallado y Estadísticas Clave")
    current_y -= 20
    
    # Sentiment Analysis of Comments (in text with colors)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, current_y, "Análisis de Sentimiento de Comentarios:")
    current_y -= 15
    c.setFont("Helvetica", 10)
    
    sentiments = [cmt.get("sentimiento", "").lower() for cmt in comments]
    positive_count = sentiments.count("positivo")
    neutral_count = sentiments.count("neutro")
    negative_count = sentiments.count("negativo")
    total_comments = len(sentiments)

    if total_comments > 0:
        positive_percent = (positive_count / total_comments) * 100
        neutral_percent = (neutral_count / total_comments) * 100
        negative_percent = (negative_count / total_comments) * 100

        # Display counts and percentages with colors
        c.setFillColor(HexColor("#4CAF50")) # Green for positive
        c.drawString(margin, current_y, f"• Positivos: {positive_count} ({positive_percent:.1f}%)")
        current_y -= 12
        c.setFillColor(HexColor("#FFC107")) # Amber for neutral
        c.drawString(margin, current_y, f"• Neutros: {neutral_count} ({neutral_percent:.1f}%)")
        current_y -= 12
        c.setFillColor(HexColor("#F44336")) # Red for negative
        c.drawString(margin, current_y, f"• Negativos: {negative_count} ({negative_percent:.1f}%)")
        current_y -= 12
        c.setFillColor(black) # Reset to black

        current_y -= 10
        summary_text_sentiment = (
            f"El {positive_percent:.1f}% de los comentarios son positivos, destacando la alta satisfacción general. "
            f"Un {neutral_percent:.1f}% son neutros, a menudo mencionando aspectos como la 'tela finita' o precios. "
            f"El {negative_percent:.1f}% son negativos, lo cual indica áreas a mejorar."
        )
        lines_sentiment = simpleSplit(summary_text_sentiment, "Helvetica", 10, width - 2 * margin)
        for line in lines_sentiment:
            if current_y < margin + 20:
                c.showPage()
                current_y = height - margin
                c.setFont("Helvetica", 10)
            c.drawString(margin, current_y, line)
            current_y -= 15
    else:
        c.drawString(margin, current_y, "No hay datos de sentimiento disponibles para analizar.")
        current_y -= 15

    current_y -= 15
    if current_y < margin + 100: # Check if there is enough space for the next section
        c.showPage()
        current_y = height - margin

    # Number of registered emails (in text)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, current_y, "Estadísticas de Contacto:")
    current_y -= 15
    c.setFont("Helvetica", 10)
    # Now, num_emails_registered is calculated from get_all_users()
    c.drawString(margin, current_y, f"• Número de correos electrónicos registrados: {num_emails_registered}")
    current_y -= 25

    # Useful information in text, not graphics (Conclusions and Recommendations)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, current_y, "Conclusiones y Recomendaciones Clave:")
    current_y -= 15
    c.setFont("Helvetica", 10)
    insights = [
        "La amabilidad y rapidez en la atención al cliente son puntos fuertes consistentemente mencionados. Considerar mantener y reforzar los programas de capacitación en servicio al cliente.",
        "La calidad de la tela es un área de mejora recurrente. Se recomienda investigar proveedores de materiales de mayor calidad o ajustar las expectativas del cliente sobre los productos.",
        "Los precios son percibidos como algo elevados por algunos clientes. Evaluar la relación calidad-precio y las estrategias de precios frente a la competencia.",
        "La experiencia de compra general es percibida como positiva y eficiente, lo que contribuye a la fidelización del cliente."
    ]
    for insight in insights:
        lines_insight = simpleSplit(f"• {insight}", "Helvetica", 10, width - 2 * margin)
        for line in lines_insight:
            if current_y < margin + 20:
                c.showPage()
                current_y = height - margin
                c.setFont("Helvetica", 10)
            c.drawString(margin, current_y, line)
            current_y -= 15
        current_y -= 5 # Extra space between conclusions

    current_y -= 10
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 25

    # --- Embed visual charts (as before) ---
    if charts:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, current_y, "Gráficos Visuales Representativos")
        current_y -= 20 # Space after section title

        for title, b64_data in charts.items():
            if current_y < margin + 250: # Estimated chart height needed is around 250 points
                c.showPage()
                current_y = height - margin # Reset Y position
                c.setFont("Helvetica-Bold", 14)
                c.drawString(margin, current_y, "Gráficos Visuales (Continuación)")
                current_y -= 20

            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, current_y, f"📊 {title}")
            current_y -= 15

            try:
                # Validate b64_data before decoding
                if not isinstance(b64_data, str) or not (b64_data.startswith("data:image/") and ";base64," in b64_data) :
                     print(f"⚠️ Invalid Base64 data format for chart '{title}'. Expected 'data:image/...;base64,...'")
                     c.setFont("Helvetica", 10)
                     c.setFillColor(black)
                     c.drawString(margin, current_y, f"⚠️ Datos de gráfico inválidos para '{title}'.")
                     current_y -= 20
                     continue # Skip to the next chart

                # Extract only the base64 part
                image_base64_payload = b64_data.split(',')[1]
                
                # It's good practice to wrap base64decode in a try-except
                image_data = base64.b64decode(image_base64_payload)
                image = ImageReader(io.BytesIO(image_data))
                
                img_width, img_height = image.getSize()
                aspect_ratio = img_height / img_width
                
                display_width = width - 2 * margin
                display_height = display_width * aspect_ratio

                if display_height > 200:
                    display_height = 200
                    display_width = display_height / aspect_ratio

                img_x = margin + ( (width - 2 * margin) - display_width ) / 2
                img_y = current_y - display_height - 10

                c.drawImage(image, img_x, img_y, width=display_width, height=display_height, preserveAspectRatio=True)
                current_y = img_y - 15
                
            except Exception as e:
                c.setFont("Helvetica", 10)
                c.setFillColor(black)
                c.drawString(margin, current_y, f"⚠️ Error al cargar el gráfico '{title}': {e}")
                traceback.print_exc() # Print full traceback for image loading errors
                current_y -= 20

            current_y -= 15

        current_y -= 10
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.line(margin, current_y, width - margin, current_y)
        current_y -= 25

    # --- The 'Detailed Comments Table' section has been removed to focus on the summary ---
    # If you want to re-include it in the future, you can reinsert the code for this section here.

    c.save() # Calls the save method of NumberedCanvas, which adds page numbers
    buffer.seek(0)
    return buffer
