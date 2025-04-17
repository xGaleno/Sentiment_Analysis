import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno del archivo .env

# Inicializa cliente Firestore usando la clave del .env
db = firestore.Client()

# === FUNCIONES DE USO ===

def add_user(name, age, email):
    doc_ref = db.collection('users').document(email)
    doc_ref.set({
        'name': name,
        'age': age,
        'email': email
    })

def get_user_by_email(email):
    doc_ref = db.collection('users').document(email)
    return doc_ref.get()

def get_all_users():
    users_ref = db.collection('users')
    return [doc.to_dict() for doc in users_ref.stream()]

def add_comment(email, comment_text, sentiment):
    user_doc = db.collection('users').document(email)
    if not user_doc.get().exists:
        return None
    db.collection('comments').add({
        'user_email': email,
        'comment_text': comment_text,
        'sentiment': sentiment,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    return True

def get_all_comments():
    comments_ref = db.collection('comments').order_by('timestamp')
    return [doc.to_dict() for doc in comments_ref.stream()]

def clear_comments():
    comments_ref = db.collection('comments')
    for doc in comments_ref.stream():
        doc.reference.delete()
