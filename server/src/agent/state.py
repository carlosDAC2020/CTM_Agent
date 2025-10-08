"""Definición del estado y contexto del agente."""

from dataclasses import dataclass, field
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from typing import Any


class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """
    my_configurable_param: str


@dataclass
class State:
    """Input state for the agent.

    Defines the initial structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    """
    messages: list[HumanMessage | AIMessage]
    next_node: str | None = None  # Para controlar el flujo entre nodos
    math_result: str | None = None  # Para almacenar resultados matemáticos
    complex_chain_result: str | None = None  # Para almacenar resultados del flujo complejo
    events: list[dict[str, Any]] = field(default_factory=list)  # Para tracking de eventos
