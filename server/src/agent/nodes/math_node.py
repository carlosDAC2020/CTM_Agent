"""Nodo que realiza operaciones matemáticas."""

from typing import Any, Dict
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage, HumanMessage
from dataclasses import asdict

from ..state import State, Context
from ..config import get_llm
from ..utils import safe_eval_math, extract_math_expression
from ..events import AgentEvent


async def math_operations(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Nodo que realiza operaciones matemáticas.
    
    Args:
        state: Estado actual del agente
        runtime: Runtime de LangGraph
        
    Returns:
        Diccionario con el resultado de la operación matemática
    """
    events = list(state.events)  # Copiar eventos existentes
    
    # Evento de inicio
    events.append(asdict(AgentEvent.node_start("math_operations", "Iniciando cálculo matemático")))
    
    last_message = state.messages[-1]
    user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    # Extraer expresión matemática del texto
    events.append(asdict(AgentEvent.step("math_operations", "extraction", "Extrayendo expresión matemática del texto")))
    events.append(asdict(AgentEvent.tool_call("math_operations", "extract_math_expression", {"text": user_input})))
    
    expression = extract_math_expression(user_input)
    events.append(asdict(AgentEvent.tool_result("math_operations", "extract_math_expression", expression)))
    
    if expression:
        try:
            events.append(asdict(AgentEvent.step("math_operations", "calculation", f"Evaluando expresión: {expression}")))
            events.append(asdict(AgentEvent.tool_call("math_operations", "safe_eval_math", {"expression": expression})))
            
            result = safe_eval_math(expression)
            events.append(asdict(AgentEvent.tool_result("math_operations", "safe_eval_math", result)))
            
            response_text = f"El resultado de {expression} es: {result}"
            events.append(asdict(AgentEvent.message("math_operations", response_text)))
            events.append(asdict(AgentEvent.node_end("math_operations", "Cálculo completado exitosamente")))
            
            return {
                "messages": [AIMessage(content=response_text)],
                "math_result": str(result),
                "events": events,
                "next_node": None
            }
        except Exception as e:
            error_msg = f"Error al calcular: {str(e)}"
            events.append(asdict(AgentEvent.error("math_operations", error_msg)))
            events.append(asdict(AgentEvent.node_end("math_operations", "Cálculo falló")))
            
            return {
                "messages": [AIMessage(content=error_msg)],
                "events": events,
                "next_node": None
            }
    else:
        # Si no se encuentra expresión, usar LLM para interpretar
        events.append(asdict(AgentEvent.step("math_operations", "llm_fallback", "No se encontró expresión, usando LLM para interpretar")))
        
        llm = get_llm()
        prompt = f"Extrae y calcula la operación matemática de: {user_input}"
        
        events.append(asdict(AgentEvent.tool_call("math_operations", "llm_interpret", {"prompt": prompt})))
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        events.append(asdict(AgentEvent.tool_result("math_operations", "llm_interpret", response.content)))
        events.append(asdict(AgentEvent.node_end("math_operations", "Interpretación por LLM completada")))
        
        return {
            "messages": [response],
            "events": events,
            "next_node": None
        }
