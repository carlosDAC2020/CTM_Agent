# src/agent/nodes/ingestion.py

from typing import Dict, Any
from ..state import ProjectState # Importamos nuestro estado

def ingest_project_info(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo de entrada del grafo.
    Confirma la recepción de los datos del proyecto y prepara el siguiente paso.
    """
    print("--- NODO: INGESTIÓN DE PROYECTO ---")
    
    # Obtenemos el título del estado actual para usarlo en el mensaje.
    title = state.get("project_title", "sin título")

    # En el futuro, aquí podrías añadir lógica para:
    # 1. Validar que project_title y project_description no estén vacíos.
    # 2. Leer los archivos de `document_paths` y procesarlos.

    # Preparamos el mensaje de confirmación para el usuario.
    confirmation_message = {
        "role": "assistant",
        "content": f"He recibido la información para el proyecto '{title}'.\n"
                   "El siguiente paso es buscar oportunidades de inversión."
    }

    # Devolvemos un diccionario para actualizar el estado.
    # En este caso, solo añadimos nuestro mensaje de confirmación al historial.
    return {"messages": [confirmation_message]}