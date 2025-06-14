import io
import os
import requests
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.lib.colors import lightgrey, black, HexColor # Importar HexColor para colores personalizados

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDzVyGvtw2qOhCzvOAzKvOCVPOC5s09bqY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def get_summary_from_gemini(text: str) -> str:
    """
    Obtiene un resumen ejecutivo de un texto dado utilizando la API de Gemini.
    Configura el modelo para generar un resumen conciso de máximo 100 palabras.
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
            "temperature": 0.7, # Controla la creatividad de la respuesta
            "maxOutputTokens": 150 # Limita la longitud máxima del resumen para asegurar concisión
        }
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        data = response.json()
        if data and 'candidates' in data and data['candidates']:
            # Extrae el texto del resumen de la respuesta de Gemini
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print("❌ La API de Gemini no devolvió la estructura de datos esperada.")
            return "No se pudo generar un resumen automático."
    except Exception as e:
        print(f"❌ Error al obtener resumen de Gemini: {e}")
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


def generate_comments_report(comments: list, filtros: dict = None, charts: dict = None) -> io.BytesIO:
    """
    Genera un informe PDF de análisis de comentarios de clientes.

    Argumentos:
        comments (list): Una lista de diccionarios, donde cada diccionario
                         representa un comentario con sus detalles.
        filtros (dict, opcional): Un diccionario de filtros aplicados al
                                  conjunto de comentarios.
        charts (dict, opcional): Un diccionario donde las claves son títulos
                                 de gráficos y los valores son datos de imagen
                                 codificados en base64 (ej. 'data:image/png;base64,...').

    Retorna:
        io.BytesIO: Un objeto de tipo BytesIO que contiene el PDF generado.
    """
    # Combina todas las respuestas para generar un resumen general
    all_text = " ".join(
        c.get("respuesta", "") for c in comments if isinstance(c.get("respuesta"), str)
    ).strip()
    if not all_text:
        all_text = "No se proporcionaron comentarios válidos para resumir."
    
    summary = get_summary_from_gemini(all_text)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    buffer = io.BytesIO()
    c = NumberedCanvas(buffer, pagesize=letter) # Usar la clase NumberedCanvas personalizada
    width, height = letter # Ancho y alto de la página (tamaño carta)
    margin = 50 # Margen a los lados de la página
    current_y = height - margin # Posición vertical actual en la página

    # --- Encabezado institucional ---
    company_name = "Alicia Modas" # Nombre de la empresa para el encabezado
    report_title = "Informe de Análisis de Comentarios" # Título del reporte

    # Si tienes un logo de la empresa, puedes cargarlo aquí.
    # Asegúrate de que el archivo del logo (ej. 'logo.png') esté en una ruta accesible en tu servidor.
    # Por ejemplo, si lo tienes en el mismo directorio que tu script:
    # logo_path = 'logo.png'
    # try:
    #     if os.path.exists(logo_path):
    #         logo = ImageReader(logo_path)
    #         # Ajusta x, y, width, height según el tamaño deseado del logo
    #         # Dibuja el logo a la derecha del título del reporte o en una esquina
    #         logo_width = 80
    #         logo_height = 40
    #         c.drawImage(logo, width - margin - logo_width, current_y - 30, width=logo_width, height=logo_height, preserveAspectRatio=True)
    # except Exception as e:
    #     print(f"Error al cargar el logo: {e}")
    #     # Opcional: Si el logo no carga, puedes mostrar un texto de marcador de posición
    #     # c.setFont("Helvetica-Bold", 10)
    #     # c.drawString(width - margin - 80, current_y - 20, "🏢 Logo Ausente")

    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin, current_y, f"{company_name}")
    current_y -= 30 # Espacio después del nombre de la empresa

    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, current_y, f"📄 {report_title}")
    current_y -= 25 # Espacio después del título del informe

    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, f"Fecha de generación: {fecha_actual}")
    current_y -= 12
    c.drawString(margin, current_y, f"Total de comentarios procesados: {len(comments)}")
    current_y -= 12
    if filtros:
        filter_text_parts = []
        for k, v in filtros.items():
            if isinstance(v, list):
                filter_text_parts.append(f"{k}: {', '.join(map(str, v))}")
            else:
                filter_text_parts.append(f"{k}: {v}")
        c.drawString(margin, current_y, f"Filtros aplicados: {', '.join(filter_text_parts)}")
        current_y -= 15

    # Línea divisoria después del encabezado
    c.setStrokeColor(HexColor("#CCCCCC")) # Un gris más claro para la línea
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 25 # Espacio después de la línea

    # --- Resumen ejecutivo automatizado por IA ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Resumen Ejecutivo Automatizado por IA")
    current_y -= 20 # Espacio después del título de sección
    c.setFont("Helvetica", 11)
    
    # Divide el resumen en líneas que se ajusten al ancho de la página
    lines = simpleSplit(summary, "Helvetica", 11, width - 2 * margin)
    for line in lines:
        if current_y < margin + 20: # Si el contenido baja del margen, mostrar nueva página
            c.showPage()
            current_y = height - margin # Reiniciar y para la nueva página
            c.setFont("Helvetica", 11) # Volver a aplicar la fuente para la nueva página
        c.drawString(margin, current_y, line)
        current_y -= 15 # Espaciado de línea

    current_y -= 10 # Espacio extra después del resumen
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.line(margin, current_y, width - margin, current_y) # Línea divisoria
    current_y -= 25 # Espacio después de la línea

    # --- Análisis Detallado y Estadísticas Clave (NUEVA SECCIÓN) ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Análisis Detallado y Estadísticas Clave")
    current_y -= 20
    
    # Análisis de Sentimiento de Comentarios (en texto con colores)
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

        # Muestra los recuentos y porcentajes con colores
        c.setFillColor(HexColor("#4CAF50")) # Verde para positivo
        c.drawString(margin, current_y, f"• Positivos: {positive_count} ({positive_percent:.1f}%)")
        current_y -= 12
        c.setFillColor(HexColor("#FFC107")) # Ámbar para neutro
        c.drawString(margin, current_y, f"• Neutros: {neutral_count} ({neutral_percent:.1f}%)")
        current_y -= 12
        c.setFillColor(HexColor("#F44336")) # Rojo para negativo
        c.drawString(margin, current_y, f"• Negativos: {negative_count} ({negative_percent:.1f}%)")
        current_y -= 12
        c.setFillColor(black) # Restablecer a negro

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
    if current_y < margin + 100: # Verificar si hay suficiente espacio para la siguiente sección
        c.showPage()
        current_y = height - margin

    # Cantidad de correos registrados (en texto)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, current_y, "Estadísticas de Contacto:")
    current_y -= 15
    c.setFont("Helvetica", 10)
    # IMPORTANTE: Debes obtener el número real de correos registrados y pasarlo aquí.
    # Por ahora, es un marcador de posición.
    num_emails_registered = 0 # Reemplaza 0 con la cantidad real de correos registrados
    c.drawString(margin, current_y, f"• Número de correos electrónicos registrados: {num_emails_registered} (Dato a proveer externamente)")
    current_y -= 25

    # Cosas que puedan ser útiles pero en texto y no gráficos (Conclusiones y Recomendaciones)
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
        current_y -= 5 # Espacio extra entre conclusiones

    current_y -= 10
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 25

    # --- Incrustar gráficos (visual, como antes) ---
    if charts:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, current_y, "Gráficos Visuales Representativos")
        current_y -= 20 # Espacio después del título de sección

        for title, b64_data in charts.items():
            if current_y < margin + 250: # Se estima que un gráfico necesita alrededor de 250 puntos de altura
                c.showPage()
                current_y = height - margin # Reinicia la posición Y
                c.setFont("Helvetica-Bold", 14)
                c.drawString(margin, current_y, "Gráficos Visuales (Continuación)")
                current_y -= 20

            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, current_y, f"📊 {title}")
            current_y -= 15

            try:
                if ',' in b64_data:
                    image_data = base64.b64decode(b64_data.split(',')[1])
                else:
                    image_data = base64.b64decode(b64_data)
                
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
                c.drawString(margin, current_y, f"⚠️ No se pudo cargar el gráfico '{title}': {e}")
                current_y -= 20

            current_y -= 15

        current_y -= 10
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.line(margin, current_y, width - margin, current_y)
        current_y -= 25

    # --- Detalle tabular de comentarios ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Detalle de Comentarios")
    current_y -= 20
    c.setFont("Helvetica", 9)

    headers = ["Fecha", "Usuario", "Pregunta", "Respuesta", "Sentimiento", "Polaridad"]
    col_widths = [70, 70, 100, 150, 60, 50]

    header_height = 18
    c.setFillColor(lightgrey)
    c.rect(margin, current_y - header_height, sum(col_widths), header_height, fill=1)
    c.setFillColor(black)

    header_y = current_y - 12
    x_offset = margin
    for i, header in enumerate(headers):
        c.drawString(x_offset, header_y, header)
        x_offset += col_widths[i]
    current_y -= header_height + 5

    row_height = 15

    for cmt in comments:
        if current_y < margin + row_height:
            c.showPage()
            current_y = height - margin
            
            c.setFillColor(lightgrey)
            c.rect(margin, current_y - header_height, sum(col_widths), header_height, fill=1)
            c.setFillColor(black)
            header_y = current_y - 12
            x_offset = margin
            for i, header in enumerate(headers):
                c.drawString(x_offset, header_y, header)
                x_offset += col_widths[i]
            current_y -= header_height + 5

        data_row = [
            cmt.get("timestamp", "")[:19],
            cmt.get("usuario", "")[:15],
            cmt.get("pregunta", ""),
            cmt.get("respuesta", ""),
            cmt.get("sentimiento", ""),
            str(cmt.get("polaridad", ""))
        ]

        x_offset = margin
        for i, value in enumerate(data_row):
            if c.stringWidth(value, "Helvetica", 9) > col_widths[i] - 5:
                while c.stringWidth(value + "...", "Helvetica", 9) > col_widths[i] - 5 and len(value) > 0:
                    value = value[:-1]
                if len(value) < len(data_row[i]):
                    value += "..."
            
            c.drawString(x_offset, current_y - 10, value)
            x_offset += col_widths[i]
        current_y -= row_height

    c.save() # Llama al método save de NumberedCanvas, que añade los números de página
    buffer.seek(0)
    return buffer