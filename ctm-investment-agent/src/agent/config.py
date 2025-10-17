# src/agent/config.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
load_dotenv()

def get_llm():
    """
    Crea y retorna una instancia configurada del modelo LLM de Google.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
        
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # Puedes cambiarlo por gemini-1.5-pro si necesitas más potencia
        api_key=api_key,
        temperature=0.8 # Una temperatura baja es buena para tareas que requieren predictibilidad
    )