# src/agent/nodes/ingestion.py

from typing import Dict, Any
from ..state import ProjectState

def ingest_project_info(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo de entrada del grafo.
    Confirma la recepción de los datos del proyecto y prepara el siguiente paso.
    IMPORTANTE: Inicializa todas las listas acumulativas si no existen.
    """
    print("--- NODO: INGESTIÓN DE PROYECTO ---")
    
    # Obtenemos el título del estado actual
    title = state.get("project_title", "sin título")

    # Preparamos el mensaje de confirmación
    confirmation_message = {
        "role": "assistant",
        "content": f"He recibido la información para el proyecto '{title}'.\n"
                   "Comenzaré con la investigación del estado del arte."
    }

    # CRÍTICO: Inicializar todas las listas acumulativas
    # Si ya existen en el estado, las mantenemos; si no, las inicializamos vacías
    return {
        "messages": [confirmation_message],
        
        # Inicializar listas acumulativas (solo si no existen)
        "investment_opportunities": state.get("investment_opportunities", []),
        "selected_opportunities": state.get("selected_opportunities", []),
        "academic_papers": state.get("academic_papers", []),
        "report_paths": state.get("report_paths", []),
        "search_queries": state.get("search_queries", []),
        "search_results": state.get("search_results", []),
        "relevant_results": state.get("relevant_results", []),
        "document_paths": state.get("document_paths", []),
    }