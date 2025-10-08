"""Multi-Node LangGraph Agent.

Este módulo define un agente con múltiples nodos especializados:
- Router para dirigir el flujo
- Nodo de operaciones matemáticas
- Nodo de flujos complejos de LangChain
- Nodo LLM general
"""

from agent.graph import graph
from agent.state import State, Context

__all__ = ["graph", "State", "Context"]
