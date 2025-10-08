"""Nodo router que dirige el flujo del agente."""

import re
from typing import Any, Dict
from langgraph.runtime import Runtime
from dataclasses import asdict

from ..state import State, Context
from ..config import MATH_KEYWORDS, COMPLEX_KEYWORDS
from ..events import AgentEvent


async def router_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Nodo router que decide qué nodo ejecutar según el mensaje del usuario.
    
    Args:
        state: Estado actual del agente
        runtime: Runtime de LangGraph
        
    Returns:
        Diccionario con el siguiente nodo a ejecutar
    """
    events = list(state.events)  # Copiar eventos existentes
    
    # Evento de inicio
    events.append(asdict(AgentEvent.node_start("router", "Analizando tipo de consulta")))
    
    last_message = state.messages[-1]
    user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    events.append(asdict(AgentEvent.step("router", "analysis", f"Analizando entrada: {user_input[:50]}...")))
    
    # Detectar si es una operación matemática
    if re.search(r'^[\d+\-*/()\ s]+$', user_input.strip()) or \
       any(word in user_input.lower() for word in MATH_KEYWORDS):
        events.append(asdict(AgentEvent.step("router", "decision", "Detectada operación matemática")))
        events.append(asdict(AgentEvent.node_end("router", "Dirigiendo a math_operations")))
        return {"next_node": "math_operations", "events": events}
    
    # Detectar si requiere un flujo complejo (RAG, búsqueda, análisis profundo)
    if any(keyword in user_input.lower() for keyword in COMPLEX_KEYWORDS):
        events.append(asdict(AgentEvent.step("router", "decision", "Detectada consulta compleja")))
        events.append(asdict(AgentEvent.node_end("router", "Dirigiendo a complex_chain")))
        return {"next_node": "complex_chain", "events": events}
    
    # Por defecto, ir al modelo simple
    events.append(asdict(AgentEvent.step("router", "decision", "Consulta general detectada")))
    events.append(asdict(AgentEvent.node_end("router", "Dirigiendo a call_model")))
    return {"next_node": "call_model", "events": events}
