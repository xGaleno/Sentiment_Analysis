from flask import request, jsonify
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
        text = data.get('text')

        if not text or not email:
            return jsonify({"error": "Text and email are required"}), 400

        user = get_user_by_email(email)
        if not user.exists:
            return jsonify({"error": "User not found"}), 404

        sentiment = analyze_sentiment(text)
        if sentiment == "Error":
            return jsonify({"error": "Sentiment analysis failed"}), 500

        success = add_comment(email, text, sentiment)
        if not success:
            return jsonify({"error": "Error saving comment"}), 500

        return jsonify({"sentiment": sentiment})

    @app.route('/api/comments', methods=['GET'])
    def comments():
        try:
            all_comments = get_all_comments()
            return jsonify(all_comments)
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
