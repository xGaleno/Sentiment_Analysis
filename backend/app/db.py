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

def add_comment(usuario, pregunta, respuesta, sentimiento, polaridad):
    db.collection('comments').add({
        'usuario': usuario,
        'pregunta': pregunta,
        'respuesta': respuesta,
        'sentimiento': sentimiento,
        'polaridad': polaridad,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

def get_all_comments():
    comments_ref = db.collection('comments').order_by('timestamp')
    return [doc.to_dict() for doc in comments_ref.stream()]

def clear_comments():
    comments_ref = db.collection('comments')
    for doc in comments_ref.stream():
        doc.reference.delete()