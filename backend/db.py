import os
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import firestore

# Cargar variables de entorno desde .env (útil en local)
load_dotenv()

# Inicialización diferida (lazy) del cliente Firestore
_firestore_client = None

def get_db():
    global _firestore_client
    if _firestore_client is None:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if not credentials_path or not os.path.exists(credentials_path):
            raise RuntimeError(f"Credenciales de Firebase no encontradas: {credentials_path}")

        # Asegura que se use la ruta relativa desde la raíz del proyecto
        absolute_path = os.path.abspath(credentials_path)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = absolute_path
        _firestore_client = firestore.Client()

    return _firestore_client

# === Funciones de usuarios ===

def add_user(name, age, email):
    db = get_db()
    db.collection('users').document(email).set({
        'name': name,
        'age': age,
        'email': email,
        'registration_date': datetime.utcnow()
    })

def get_user_by_email(email):
    db = get_db()
    return db.collection('users').document(email).get()

def get_all_users():
    db = get_db()
    return [doc.to_dict() for doc in db.collection('users').stream()]

def delete_user_by_email(email):
    db = get_db()
    db.collection('users').document(email).delete()

# === Funciones de comentarios ===

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
    return [doc.to_dict() for doc in db.collection('comments').order_by('timestamp').stream()]

def clear_comments():
    db = get_db()
    for doc in db.collection('comments').stream():
        doc.reference.delete()

def delete_comments_by_email(email):
    db = get_db()
    comments = db.collection('comments').where('usuario', '==', email).stream()
    for comment in comments:
        comment.reference.delete()
