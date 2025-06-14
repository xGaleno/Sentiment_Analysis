from flask import request, jsonify, render_template, send_file
from datetime import datetime, timezone
from .db import (
    add_user, get_user_by_email, get_all_users,
    add_comment, get_all_comments, clear_comments
)
from .app.services.sentiment_analysis import analyze_sentiment
from .app.services.generate_report import generate_comments_report

import smtplib
import threading
from email.mime.text import MIMEText
from email.header import Header
import traceback
import time

correos_enviados_log = []

def register_routes(app):
    # === RUTAS DE FRONTEND ===
    @app.route("/")
    def main():
        return render_template("main.html")

    @app.route("/empresa_analisis")
    def empresa_analisis():
        return render_template("empresa_analisis.html")

    @app.route("/empresa_login")
    def empresa_login():
        return render_template("empresa_login.html")

    @app.route("/usuario")
    def usuario():
        return render_template("usuario.html")

    @app.route("/agradecimiento")
    def agradecimiento():
        return render_template("agradecimiento.html")

    # === REGISTRO DE USUARIO ===
    @app.route('/api/register_user', methods=['POST'])
    def register_user():
        data = request.json
        name, age, email = data.get('name'), data.get('age'), data.get('email')

        if not name or not age or not email:
            return jsonify({"error": "All fields (name, age, email) are required"}), 400

        if get_user_by_email(email).exists:
            return jsonify({"error": "Email already exists"}), 409

        try:
            add_user(name, age, email)
            return jsonify({"message": "User registered successfully"}), 201
        except Exception as e:
            return jsonify({"error": f"Error registering user: {str(e)}"}), 500

    # === ANÁLISIS DE SENTIMIENTO ===
    @app.route('/api/sentiment_analysis', methods=['POST'])
    def sentiment_analysis():
        data = request.json
        email = data.get('email')
        respuestas = data.get('respuestas')

        if not email or not respuestas:
            return jsonify({"error": "Email and respuestas are required"}), 400

        if not get_user_by_email(email).exists:
            return jsonify({"error": "User not found"}), 404

        today = datetime.now(timezone.utc).date()
        user_comments = get_all_comments()
        for c in user_comments:
            if c.get("usuario") == email:
                ts = c.get("timestamp")
                if ts and hasattr(ts, 'date') and ts.date() == today:
                    return jsonify({"error": "Solo se permite una opinión por día."}), 429

        resultados = []
        for item in respuestas:
            pregunta = item.get("pregunta")
            texto = item.get("respuesta")
            if not texto or not pregunta:
                continue

            sentimiento = analyze_sentiment(texto)
            if sentimiento == "Error":
                sentimiento = "nulo"
                polaridad = 0.0
            else:
                polaridad = 0.5 if sentimiento == "positivo" else -0.5 if sentimiento == "negativo" else 0.0

            add_comment(email, pregunta, texto, sentimiento, polaridad)

            resultados.append({
                "pregunta": pregunta,
                "respuesta": texto,
                "sentimiento": sentimiento,
                "polaridad": polaridad
            })

        try:
            threading.Thread(target=send_email, args=(email,)).start()
        except Exception as e:
            print("Error al lanzar hilo de correo:", e)

        return jsonify(resultados)

    # === COMENTARIOS ===
    @app.route('/api/comments', methods=['GET'])
    def comments():
        start = time.time()
        print("📥 [API] /api/comments – inicio")
        try:
            comments = get_all_comments()
            formatted = []
            for c in comments:
                ts = c.get("timestamp")
                if not ts or not c.get("sentimiento"):
                    continue
                ts_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
                formatted.append({
                    "usuario": c.get("usuario"),
                    "pregunta": c.get("pregunta"),
                    "respuesta": c.get("respuesta"),
                    "sentimiento": c.get("sentimiento"),
                    "polaridad": c.get("polaridad"),
                    "timestamp": ts_str
                })
            elapsed = time.time() - start
            print(f"✅ [API] /api/comments – fin en {elapsed:.2f}s")
            return jsonify(formatted)
        except Exception as e:
            print("❌ Error en /api/comments:")
            traceback.print_exc()
            return jsonify({"error": f"Error getting comments: {str(e)}"}), 500

    @app.route('/api/clear_comments', methods=['DELETE'])
    def clear_all_comments():
        try:
            clear_comments()
            return jsonify({"message": "All comments cleared successfully."}), 200
        except Exception as e:
            return jsonify({"error": f"Error clearing comments: {str(e)}"}), 500

    # === USUARIOS ===
    @app.route('/api/users', methods=['GET'])
    def users():
        start = time.time()
        print("📥 [API] /api/users – inicio")
        try:
            users = get_all_users()
            elapsed = time.time() - start
            print(f"✅ [API] /api/users – fin en {elapsed:.2f}s (total {len(users)} usuarios)")
            return jsonify(users)
        except Exception as e:
            print("❌ [API] /api/users error:")
            traceback.print_exc()
            return jsonify({"error": f"Error getting users: {str(e)}"}), 500

    @app.route('/api/delete_user/<email>', methods=['DELETE'])
    def delete_user(email):
        try:
            from .db import delete_user_by_email, delete_comments_by_email
            delete_user_by_email(email)
            delete_comments_by_email(email)
            return jsonify({"message": f"Usuario {email} y sus comentarios fueron eliminados."}), 200
        except Exception as e:
            return jsonify({"error": f"Error al eliminar usuario: {str(e)}"}), 500

    @app.route('/api/check_user', methods=['POST'])
    def check_user():
        email = request.json.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400
        user = get_user_by_email(email)
        if not user.exists:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User exists"}), 200

    @app.route('/api/send_confirmation_email', methods=['POST'])
    def send_confirmation_email():
        email = request.json.get('email')
        if not email:
            return jsonify({"error": "Email is required"}), 400
        try:
            send_email(email)
            return jsonify({"message": "Confirmation email sent successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Error sending email: {str(e)}"}), 500

    @app.route('/api/generate_report', methods=['POST', 'OPTIONS'])
    def generate_report():
        if request.method == 'OPTIONS':
            return '', 200
        comentarios = request.get_json().get("comentarios", [])
        if not comentarios:
            return jsonify({"error": "No se enviaron comentarios"}), 400

        buffer = generate_comments_report(comentarios)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='reporte_comentarios.pdf'
        )

    def send_email(recipient_email):
        sender_email = "aliciamodas.diha@gmail.com"
        sender_password = "addt58Y0~nFA"
        subject = "¡Gracias por tu confianza en Alicia Modas!"
        body = (
            "Hola,\n\n"
            "Gracias por compartir tu opinión con Alicia Modas.\n"
            "Tu participación es clave para seguir mejorando.\n\n"
            "Atentamente,\nEquipo de Alicia Modas"
        )

        msg = MIMEText(body, _charset='utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())

            # Agregar al log
            correos_enviados_log.append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "destinatario": recipient_email,
                "asunto": subject,
                "estado": "✅ Enviado"
            })
        except Exception as e:
            correos_enviados_log.append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "destinatario": recipient_email,
                "asunto": subject,
                "estado": f"❌ Error: {str(e)}"
            })
            print(f"Error enviando email: {e}")
            raise e
        
    @app.route('/api/correos_enviados', methods=['GET'])
    def correos_enviados():
        return jsonify(correos_enviados_log)