import os
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import firestore

# Cargar variables de entorno
load_dotenv()

# Cliente Firestore con inicialización diferida (lazy)
_firestore_client = None

def get_db():
    """Devuelve una instancia única del cliente de Firestore."""
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client

# === Funciones de usuarios ===

def add_user(name, age, email):
    """Agrega un nuevo usuario a la colección 'users'."""
    db = get_db()
    db.collection('users').document(email).set({
        'name': name,
        'age': age,
        'email': email,
        'registration_date': datetime.utcnow()
    })

def get_user_by_email(email):
    """Obtiene un documento de usuario por su email."""
    db = get_db()
    return db.collection('users').document(email).get()

def get_all_users():
    """Devuelve todos los usuarios registrados como lista de diccionarios."""
    db = get_db()
    return [doc.to_dict() for doc in db.collection('users').stream()]

# === Funciones de comentarios ===

def add_comment(usuario, pregunta, respuesta, sentimiento, polaridad):
    """Agrega un comentario con análisis de sentimiento."""
    db = get_db()
    db.collection('comments').add({
        'usuario': usuario,
        'pregunta': pregunta,
        'respuesta': respuesta,
        'sentimiento': sentimiento,
        'polaridad': polaridad,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

def get_all_comments():
    """Devuelve todos los comentarios ordenados por fecha."""
    db = get_db()
    return [doc.to_dict() for doc in db.collection('comments').order_by('timestamp').stream()]

def clear_comments():
    """Elimina todos los documentos de la colección 'comments'."""
    db = get_db()
    for doc in db.collection('comments').stream():
        doc.reference.delete()
