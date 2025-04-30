
from flask import request, jsonify, render_template, send_file
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from io import BytesIO

from .db import (
    add_user,
    get_user_by_email,
    get_all_users,
    add_comment,
    get_all_comments,
    clear_comments
)
from .services.sentiment_analysis import analyze_sentiment
from .services.generate_report import generate_comments_report


def register_routes(app):
    # === Usuarios ===
    @app.route('/api/register_user', methods=['POST'])
    def register_user():
        data = request.json
        name = data.get('name')
        age = data.get('age')
        email = data.get('email')

        if not name or not age or not email:
            return jsonify({"error": "All fields (name, age, email) are required"}), 400

        existing_user = get_user_by_email(email)
        if existing_user.exists:
            return jsonify({"error": "Email already exists"}), 409

        try:
            add_user(name, age, email)
            return jsonify({"message": "User registered successfully"}), 201
        except Exception as e:
            return jsonify({"error": f"Error registering user: {str(e)}"}), 500

    @app.route('/api/users', methods=['GET'])
    def users():
        try:
            all_users = get_all_users()
            return jsonify(all_users)
        except Exception as e:
            return jsonify({"error": f"Error getting users: {str(e)}"}), 500

    # === Comentarios ===
    @app.route('/api/comments', methods=['GET'])
    def comments():
        try:
            all_comments_raw = get_all_comments()
            formatted_comments = []

            for comment in all_comments_raw:
                if not comment.get("timestamp") or not comment.get("sentimiento"):
                    continue

                timestamp = comment["timestamp"]
                if isinstance(timestamp, datetime):
                    timestamp_str = timestamp.isoformat()
                elif hasattr(timestamp, "isoformat"):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)

                formatted_comments.append({
                    "usuario": comment.get("usuario"),
                    "pregunta": comment.get("pregunta"),
                    "respuesta": comment.get("respuesta"),
                    "sentimiento": comment.get("sentimiento"),
                    "polaridad": comment.get("polaridad"),
                    "timestamp": timestamp_str
                })

            return jsonify(formatted_comments)
        except Exception as e:
            return jsonify({"error": f"Error getting comments: {str(e)}"}), 500

    @app.route('/api/clear_comments', methods=['DELETE'])
    def clear_all_comments():
        try:
            clear_comments()
            return jsonify({"message": "All comments cleared successfully."}), 200
        except Exception as e:
            return jsonify({"error": f"Error clearing comments: {str(e)}"}), 500

    # === Análisis de Sentimiento ===
    @app.route('/api/sentiment_analysis', methods=['POST'])
    def sentiment_analysis():
        data = request.json
        email = data.get('email')
        respuestas = data.get('respuestas')

        if not email or not respuestas:
            return jsonify({"error": "Email and respuestas are required"}), 400

        user = get_user_by_email(email)
        if not user.exists:
            return jsonify({"error": "User not found"}), 404

        resultados = []
        for item in respuestas:
            pregunta = item.get("pregunta")
            texto = item.get("respuesta")

            if not texto or not pregunta:
                continue

            sentimiento = analyze_sentiment(texto)
            if sentimiento == "Error":
                continue

            polaridad = 0.0
            if sentimiento == "positivo":
                polaridad = 0.5
            elif sentimiento == "negativo":
                polaridad = -0.5

            add_comment(email, pregunta, texto, sentimiento, polaridad)

            resultados.append({
                "pregunta": pregunta,
                "respuesta": texto,
                "sentimiento": sentimiento,
                "polaridad": polaridad
            })

        return jsonify(resultados)

    # === Reporte PDF desde frontend ===
    @app.route('/api/generate_report', methods=['POST'])
    def generate_report():
        try:
            data = request.get_json()
            comentarios = data.get("comentarios", [])
            if not comentarios:
                return jsonify({"error": "No se enviaron comentarios"}), 400

            buffer = generate_comments_report(comentarios)
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='reporte_comentarios.pdf'
            )
        except Exception as e:
            print("Error generando el PDF:", e)
            return jsonify({"error": "No se pudo generar el reporte"}), 500

    # === Otros ===
    @app.route('/api/send_confirmation_email', methods=['POST'])
    def send_confirmation_email():
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        try:
            send_email(email)
            return jsonify({"message": "Confirmation email sent successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Error sending email: {str(e)}"}), 500

    @app.route('/agradecimiento')
    def agradecimiento():
        return render_template("agradecimiento.html")


def send_email(recipient_email):
    sender_email = "aliciamodas.diha@gmail.com"
    sender_password = "kdsczissnqdgbpwn"

    subject = "¡Gracias por tu confianza en Alicia Modas!"
    body = (
            "Hola,\n\n"
            "Queremos agradecerte sinceramente por compartir tu opinión con Alicia Modas.\n"
            "Tu participación es fundamental para ayudarnos a seguir creciendo y ofrecerte siempre lo mejor en moda y estilo.\n\n"
            "Nuestro compromiso en Mendoza, Argentina, es brindarte experiencias únicas y productos de calidad.\n\n"
            "¡Gracias por ser parte de nuestra comunidad!\n\n"
            "Atentamente,\n"
            "Equipo de Alicia Modas"
        )

    msg = MIMEText(body, _charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender_email
    msg['To'] = recipient_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
