import os
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import firestore
from google.oauth2 import service_account

# Cargar variables de entorno desde .env
load_dotenv()

_firestore_client = None

def get_db():
    """Inicializa y devuelve el cliente de Firestore usando tu JSON local si la ruta env falla."""
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client

    # 1) Intentar ruta de env
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()

    # 2) Si creds_path existe pero no es un archivo válido, usar fallback
    if creds_path and not os.path.isfile(creds_path):
        fallback = os.path.join(os.path.dirname(__file__), "keys", "firebase-credentials.json")
        if os.path.isfile(fallback):
            print(f"⚠️ Ruta env inválida ({creds_path}); usando JSON local: {fallback}")
            creds_path = fallback
        else:
            raise FileNotFoundError(
                "❌ GOOGLE_APPLICATION_CREDENTIALS apunta a un archivo inexistente "
                f"({creds_path}) y no hay JSON en backend/keys."
            )

    # 3) Si no definiste creds_path en env o quedó vacío, probar fallback directo
    if not creds_path:
        fallback = os.path.join(os.path.dirname(__file__), "keys", "firebase-credentials.json")
        if os.path.isfile(fallback):
            creds_path = fallback
            print(f"⚠️ No se definió env; usando fallback directo: {creds_path}")
        else:
            raise FileNotFoundError(
                "❌ No se encontró credenciales: define GOOGLE_APPLICATION_CREDENTIALS "
                "o coloca el JSON en backend/keys/firebase-credentials.json"
            )

    # 4) Cargar credenciales explícitamente y crear el cliente
    creds = service_account.Credentials.from_service_account_file(creds_path)
    _firestore_client = firestore.Client(
        credentials=creds,
        project=creds.project_id
    )
    print("✅ Cliente Firestore inicializado correctamente con credenciales de archivo.")
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
    # Limitar a 50 para evitar timeouts/memoria en Render Free
    return [doc.to_dict() for doc in db.collection('users').limit(50).stream()]


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
    # Ordenar y limitar a 50 para mejorar rendimiento
    return [doc.to_dict()
            for doc in db.collection('comments')
                         .order_by('timestamp')
                         .limit(50)
                         .stream()]


def clear_comments():
    db = get_db()
    for doc in db.collection('comments').stream():
        doc.reference.delete()


def delete_comments_by_email(email):
    db = get_db()
    comments = db.collection('comments').where('usuario', '==', email).stream()
    for comment in comments:
        comment.reference.delete()
