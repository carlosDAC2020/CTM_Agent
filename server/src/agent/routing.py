"""Funciones de enrutamiento condicional del grafo."""

from .state import State


def route_after_router(state: State) -> str:
    """Función de enrutamiento condicional después del nodo router.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Nombre del siguiente nodo a ejecutar
    """
    return state.next_node or "call_model"
