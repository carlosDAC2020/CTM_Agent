# src/agent/state.py

from typing import List, TypedDict
from langchain_core.messages import HumanMessage, AIMessage

class ProjectState(TypedDict):
    """
    Representa el estado completo de un proyecto a lo largo del tiempo.
    Esta es la memoria principal de nuestro grafo.
    """
    # --- Información de Entrada ---
    project_title: str
    project_description: str
    document_paths: List[str] # Lista de rutas a documentos locales

    # --- Resultados de los Nodos (se irán llenando) ---
    investment_opportunities: List[dict]
    selected_opportunities: List[dict]
    academic_papers: List[dict]
    improvement_report: str

    # --- Historial de Conversación ---
    messages: list[HumanMessage | AIMessage]