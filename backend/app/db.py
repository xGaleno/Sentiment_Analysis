import os
from google.cloud import firestore
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # Carga variables de entorno

# Lazy client initializer
_firestore_client = None

def get_db():
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client

# === FUNCIONES DE USO ===

def add_user(name, age, email):
    db = get_db()
    doc_ref = db.collection('users').document(email)
    doc_ref.set({
        'name': name,
        'age': age,
        'email': email,
        'registration_date': datetime.utcnow()
    })

def get_user_by_email(email):
    db = get_db()
    doc_ref = db.collection('users').document(email)
    return doc_ref.get()

def get_all_users():
    db = get_db()
    users_ref = db.collection('users')
    return [doc.to_dict() for doc in users_ref.stream()]

def add_comment(usuario, pregunta, respuesta, sentimiento, polaridad):
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
    db = get_db()
    comments_ref = db.collection('comments').order_by('timestamp')
    return [doc.to_dict() for doc in comments_ref.stream()]

def clear_comments():
    db = get_db()
    comments_ref = db.collection('comments')
    for doc in comments_ref.stream():
        doc.reference.delete()
