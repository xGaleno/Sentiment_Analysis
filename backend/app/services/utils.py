import re
from tensorflow.keras.preprocessing.text import Tokenizer # type: ignore

MAX_LENGTH = 200
tokenizer = Tokenizer(num_words=10000)  # Reemplaza con tu vocabulario específico

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text