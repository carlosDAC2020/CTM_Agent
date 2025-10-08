"""Configuración del agente y modelos LLM."""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Cargar variables de entorno
load_dotenv()

# Configuración del modelo LLM
def get_llm():
    """Retorna una instancia configurada del modelo LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GEMINI_API_KEY")
    )

# Palabras clave para detección de intención
MATH_KEYWORDS = ['calcular', 'calcula', 'matemática', 'suma', 'resta', 'multiplica', 'divide']
COMPLEX_KEYWORDS = ['analiza', 'busca', 'investiga', 'compara', 'resume', 'documento', 'rag', 'búsqueda']
