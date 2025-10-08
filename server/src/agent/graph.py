"""LangGraph multi-node agent graph.

Este módulo define el grafo principal del agente con múltiples nodos especializados:
- Router: Dirige el flujo según el tipo de consulta
- LLM Node: Respuestas generales usando el modelo LLM
- Math Node: Operaciones matemáticas seguras
- Complex Chain: Flujos complejos multi-paso de LangChain
"""

from __future__ import annotations

from langgraph.graph import StateGraph

from agent.state import State, Context
from agent.nodes import router_node, call_model, math_operations, complex_chain
from agent.routing import route_after_router


def build_graph() -> StateGraph:
    """Construye y retorna el grafo compilado del agente.
    
    Returns:
        Grafo compilado listo para ejecutar
    """
    builder = StateGraph(State, context_schema=Context)
    
    # Agregar todos los nodos
    builder.add_node("router", router_node)
    builder.add_node("call_model", call_model)
    builder.add_node("math_operations", math_operations)
    builder.add_node("complex_chain", complex_chain)
    
    # Definir el flujo
    builder.add_edge("__start__", "router")
    builder.add_conditional_edges(
        "router",
        route_after_router,
        {
            "call_model": "call_model",
            "math_operations": "math_operations",
            "complex_chain": "complex_chain"
        }
    )
    
    # Todos los nodos terminan en __end__
    builder.add_edge("call_model", "__end__")
    builder.add_edge("math_operations", "__end__")
    builder.add_edge("complex_chain", "__end__")
    
    return builder.compile(name="Multi-Node Agent")


# Exportar el grafo compilado
graph = build_graph()
