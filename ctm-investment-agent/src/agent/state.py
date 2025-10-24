# src/agent/state.py

from typing import List, TypedDict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage

class ProjectState(TypedDict, total=False):
    """
    Representa el estado completo de un proyecto a lo largo del tiempo.
    """
    # --- ID de Ejecución ---
    thread_id: str

    # --- Información de Entrada ---
    project_title: str
    project_description: str
    document_paths: List[str]

    # --- Búsqueda de Información ---
    search_queries: List[str]
    search_results: List[dict]
    relevant_results: List[dict]

    # --- Resultados de los Nodos ---
    all_opportunities_history: List[dict]
    investment_opportunities: List[dict]
    selected_opportunities: List[dict]
    
    academic_papers: List[dict]
    improvement_report: Optional[str]
    report_paths: List[str]

    # --- Clave Temporal para Interrupción ---
    user_selection: Any

    # --- Historial de Conversación ---
    messages: List[HumanMessage | AIMessage]

    # ---- Routing de acciones ---------------
    next_action: Optional[str]
    action_input: Any
    report_type: Optional[str]


def create_initial_state(project_title: str, project_description: str) -> ProjectState:
    """
    Crea un estado inicial con todos los campos correctamente inicializados.
    """
    return {
        "project_title": project_title,
        "project_description": project_description,
        "document_paths": [],
        "search_queries": [],
        "search_results": [],
        "relevant_results": [],
        "all_opportunities_history": [],  # ✅ Historial completo
        "investment_opportunities": [],   # ✅ Oportunidades de la última búsqueda
        "selected_opportunities": [],      # ✅ Seleccionadas para análisis
        "academic_papers": [],
        "improvement_report": None,
        "report_paths": [],
        "user_selection": None,
        "messages": [],
        "next_action": None,
        "action_input": None,
        "report_type": None,
    }