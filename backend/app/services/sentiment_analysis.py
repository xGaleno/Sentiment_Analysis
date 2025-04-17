import requests
import json

def analyze_sentiment(text):
    # URL de la API con tu clave
    api_key = "AIzaSyD6e8l8vNIvp_8dgNyeG5DGCTyF-xHYUK0"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Ajustar el payload para que la API interprete el análisis de sentimiento
    payload = {
        "contents": [
            {
                "parts": [{"text": f"Analiza el sentimiento del siguiente comentario: '{text}'"}]
            }
        ]
    }
    
    try:
        # Enviar la solicitud a la API de Gemini
        response = requests.post(url, headers=headers, json=payload)
        
        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            sentiment_data = response.json()
            generated_text = sentiment_data['candidates'][0]['content']['parts'][0]['text']
            
            # Simplificar el análisis de sentimiento
            if "positivo" in generated_text.lower():
                return "positivo"
            elif "negativo" in generated_text.lower():
                return "negativo"
            else:
                return "neutro"
        
        print(f"Error {response.status_code}: {response.reason}")
        print("Contenido de la respuesta:", response.text)
        return "Error al obtener el análisis de sentimiento"
    
    except requests.RequestException as e:
        print("Error de conexión o solicitud:", e)
        return "Error de conexión"
