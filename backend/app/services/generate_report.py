import io
import os
import requests
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.lib.colors import lightgrey, black

# La API_KEY se deja vacía; el entorno Canvas la proporcionará automáticamente en tiempo de ejecución.
API_KEY = os.getenv("GEMINI_API_KEY", "")
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
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter # Ancho y alto de la página (tamaño carta)
    margin = 50 # Margen a los lados de la página
    current_y = height - margin # Posición vertical actual en la página

    # --- Encabezado institucional ---
    company_name = "Alicia Modas" # Nombre de la empresa para el encabezado

    # Posición para el logo (si se proporciona)
    # Si tienes un logo de la empresa, puedes cargarlo aquí.
    # Asegúrate de que el archivo del logo (ej. 'logo.png') esté en una ruta accesible.
    # logo_path = 'path/to/your/logo.png' # Reemplaza con la ruta real de tu logo
    # try:
    #     if os.path.exists(logo_path):
    #         logo = ImageReader(logo_path)
    #         # Ajusta x, y, width, height según el tamaño deseado del logo
    #         c.drawImage(logo, margin, current_y - 30, width=80, height=40, preserveAspectRatio=True)
    #     else:
    #         c.setFont("Helvetica-Bold", 10)
    #         c.drawString(margin, current_y - 20, "🏢 Logo Empresa")
    # except Exception as e:
    #     print(f"Error al cargar el logo: {e}")
    #     c.setFont("Helvetica-Bold", 10)
    #     c.drawString(margin, current_y - 20, "🏢 Logo Empresa (Error)")

    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin, current_y, f"{company_name}")
    current_y -= 30 # Espacio después del nombre de la empresa

    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, current_y, "📄 Informe de Análisis de Comentarios")
    current_y -= 25 # Espacio después del título del informe

    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, f"Fecha de generación: {fecha_actual}")
    current_y -= 12
    c.drawString(margin, current_y, f"Total de comentarios procesados: {len(comments)}")
    current_y -= 12
    if filtros:
        filter_text = ", ".join([f"{k}: {v}" for k, v in filtros.items()])
        c.drawString(margin, current_y, f"Filtros aplicados: {filter_text}")
        current_y -= 15

    # Línea divisoria después del encabezado
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
        # Verifica si hay suficiente espacio para la línea actual, si no, salta a una nueva página
        if current_y < margin + 20: # Margen inferior mínimo para texto
            c.showPage()
            current_y = height - margin # Reinicia la posición Y para la nueva página
            c.setFont("Helvetica", 11) # Reestablece la fuente después de cambiar de página
        c.drawString(margin, current_y, line)
        current_y -= 15 # Espacio entre líneas

    current_y -= 10 # Espacio extra después del resumen
    c.line(margin, current_y, width - margin, current_y) # Línea divisoria
    current_y -= 25 # Espacio después de la línea

    # --- Gráficos visuales representativos ---
    if charts:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, current_y, "Gráficos Representativos")
        current_y -= 20 # Espacio después del título de sección

        for title, b64_data in charts.items():
            # Verifica si hay suficiente espacio para el gráfico en la página actual
            # Se estima que un gráfico necesita alrededor de 250 puntos de altura
            if current_y < margin + 250:
                c.showPage()
                current_y = height - margin # Reinicia la posición Y para la nueva página
                c.setFont("Helvetica-Bold", 14) # Reestablece el título de sección
                c.drawString(margin, current_y, "Gráficos Representativos (Continuación)")
                current_y -= 20

            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, current_y, f"📊 {title}")
            current_y -= 15 # Espacio después del título del gráfico

            try:
                # Decodifica los datos de la imagen base64
                if ',' in b64_data: # Si es una URL de datos (ej. "data:image/png;base64,...")
                    image_data = base64.b64decode(b64_data.split(',')[1])
                else: # Si es solo la cadena base64 pura
                    image_data = base64.b64decode(b64_data)
                
                image = ImageReader(io.BytesIO(image_data))
                
                # Obtiene las dimensiones originales de la imagen
                img_width, img_height = image.getSize()
                aspect_ratio = img_height / img_width
                
                # Calcula las dimensiones de visualización para que quepa en la página
                # y mantenga la relación de aspecto. El ancho máximo es el ancho de la página - 2*margen.
                display_width = width - 2 * margin
                display_height = display_width * aspect_ratio

                # Si la altura calculada es demasiado grande, escala aún más para que se ajuste
                if display_height > 200: # Altura máxima deseada para un gráfico
                    display_height = 200
                    display_width = display_height / aspect_ratio

                # Centra la imagen horizontalmente
                img_x = margin + ( (width - 2 * margin) - display_width ) / 2
                img_y = current_y - display_height - 10 # Posición Y del gráfico, 10 pts de buffer

                # Dibuja la imagen en el lienzo
                c.drawImage(image, img_x, img_y, width=display_width, height=display_height, preserveAspectRatio=True)
                current_y = img_y - 15 # Mueve la posición Y después de dibujar la imagen
                
            except Exception as e:
                c.setFont("Helvetica", 10)
                c.setFillColor(black)
                c.drawString(margin, current_y, f"⚠️ No se pudo cargar el gráfico '{title}': {e}")
                current_y -= 20 # Espacio para el mensaje de error

            current_y -= 15 # Espacio entre gráficos

        current_y -= 10
        c.line(margin, current_y, width - margin, current_y) # Línea divisoria
        current_y -= 25 # Espacio después de la línea

    # --- Detalle tabular de comentarios ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Detalle de Comentarios")
    current_y -= 20 # Espacio después del título de sección
    c.setFont("Helvetica", 9) # Fuente más pequeña para el contenido de la tabla

    headers = ["Fecha", "Usuario", "Pregunta", "Respuesta", "Sentimiento", "Polaridad"]
    # Anchos de columna ajustados para un mejor ajuste del contenido
    col_widths = [70, 70, 100, 150, 60, 50] # La suma debe ser <= (width - 2*margin)

    # Dibuja el fondo gris claro para los encabezados de la tabla
    header_height = 18
    c.setFillColor(lightgrey) # Establece el color de relleno a gris claro
    c.rect(margin, current_y - header_height, sum(col_widths), header_height, fill=1) # Dibuja el rectángulo
    c.setFillColor(black) # Restablece el color de relleno a negro para el texto

    # Dibuja los encabezados de la tabla
    header_y = current_y - 12 # Posición Y para el texto de los encabezados
    x_offset = margin
    for i, header in enumerate(headers):
        c.drawString(x_offset, header_y, header)
        x_offset += col_widths[i]
    current_y -= header_height + 5 # Mueve la posición Y después de los encabezados (más un poco de padding)

    row_height = 15 # Altura para cada fila de la tabla

    for cmt in comments:
        # Verifica si hay suficiente espacio para la fila actual, si no, salta a una nueva página
        if current_y < margin + row_height:
            c.showPage()
            current_y = height - margin # Reinicia la posición Y para la nueva página
            
            # Vuelve a dibujar el encabezado de la tabla en la nueva página
            c.setFillColor(lightgrey)
            c.rect(margin, current_y - header_height, sum(col_widths), header_height, fill=1)
            c.setFillColor(black)
            header_y = current_y - 12
            x_offset = margin
            for i, header in enumerate(headers):
                c.drawString(x_offset, header_y, header)
                x_offset += col_widths[i]
            current_y -= header_height + 5

        # Prepara los datos de la fila, asegurando truncamiento para que se ajusten a la celda
        data_row = [
            cmt.get("timestamp", "")[:19], # Trunca fecha/hora
            cmt.get("usuario", "")[:15], # Trunca usuario
            cmt.get("pregunta", ""), # Se manejará el truncamiento dinámicamente
            cmt.get("respuesta", ""), # Se manejará el truncamiento dinámicamente
            cmt.get("sentimiento", ""),
            str(cmt.get("polaridad", ""))
        ]

        x_offset = margin
        for i, value in enumerate(data_row):
            # Truncamiento dinámico con "..." si el texto es demasiado largo para la columna
            if c.stringWidth(value, "Helvetica", 9) > col_widths[i] - 5: # 5 pts de padding
                while c.stringWidth(value + "...", "Helvetica", 9) > col_widths[i] - 5 and len(value) > 0:
                    value = value[:-1]
                if len(value) < len(data_row[i]): # Solo añade "..." si hubo truncamiento
                    value += "..."
            
            c.drawString(x_offset, current_y - 10, value) # 10 pts para alineación vertical en la celda
            x_offset += col_widths[i]
        current_y -= row_height # Mueve la posición Y para la siguiente fila

    # --- Paginación automática y números de página ---
    c.showPage() # Fuerza una nueva página para asegurar que la numeración se dibuje correctamente en la última página.

    # Obtiene el número total de páginas después de que se ha generado todo el contenido
    total_pages = c.getPageNumber()
    for i in range(1, total_pages + 1):
        c.setPageNumber(i) # Establece la página actual para dibujar el texto
        c.setFont("Helvetica", 9)
        # Dibuja el número de página centrado en el pie de página
        c.drawCentredString(width / 2, margin / 2, f"Página {i} de {total_pages}")
        
        # Necesario para avanzar a la siguiente página para dibujar en ella el número de página.
        # Si esta no es la última página, showPage() avanzará el lienzo a la siguiente.
        # Si es la última página, simplemente termina la página actual.
        if i < total_pages:
            c.showPage() 

    c.save() # Guarda el contenido del lienzo en el buffer
    buffer.seek(0) # Mueve el puntero al inicio del buffer para que pueda ser leído
    return buffer