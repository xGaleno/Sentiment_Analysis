from flask import request, jsonify, render_template
from datetime import datetime
from .db import (
    add_user,
    get_user_by_email,
    get_all_users,
    add_comment,
    get_all_comments,
    clear_comments
)
from .services.sentiment_analysis import analyze_sentiment

def register_routes(app):

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

    @app.route('/api/comments', methods=['GET'])
    def comments():
        try:
            all_comments_raw = get_all_comments()
            formatted_comments = []

            for comment in all_comments_raw:
                if not comment.get("timestamp") or not comment.get("sentimiento"):
                    print("Comentario omitido por estar incompleto:", comment)
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

    @app.route('/api/users', methods=['GET'])
    def users():
        try:
            all_users = get_all_users()
            return jsonify(all_users)
        except Exception as e:
            return jsonify({"error": f"Error getting users: {str(e)}"}), 500

    @app.route('/agradecimiento')
    def agradecimiento():
        return render_template("agradecimiento.html")
