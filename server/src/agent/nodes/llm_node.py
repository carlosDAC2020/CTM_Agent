"""Nodo simple que llama al modelo LLM."""

from typing import Any, Dict
from langgraph.runtime import Runtime
from dataclasses import asdict

from ..state import State, Context
from ..config import get_llm
from ..events import AgentEvent


async def call_model(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Nodo simple que llama al modelo LLM.
    
    Args:
        state: Estado actual del agente
        runtime: Runtime de LangGraph
        
    Returns:
        Diccionario con la respuesta del modelo
    """
    events = list(state.events)  # Copiar eventos existentes
    
    # Evento de inicio
    events.append(asdict(AgentEvent.node_start("call_model", "Llamando al modelo LLM")))
    
    events.append(asdict(AgentEvent.step("call_model", "llm_call", "Enviando mensajes al modelo")))
    events.append(asdict(AgentEvent.tool_call("call_model", "gemini_llm", {"messages_count": len(state.messages)})))
    
    llm = get_llm()
    response = await llm.ainvoke(state.messages)
    
    events.append(asdict(AgentEvent.tool_result("call_model", "gemini_llm", response.content)))
    events.append(asdict(AgentEvent.message("call_model", response.content)))
    events.append(asdict(AgentEvent.node_end("call_model", "Respuesta del LLM completada")))
    
    return {"messages": [response], "events": events, "next_node": None}
