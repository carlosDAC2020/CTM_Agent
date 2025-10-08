"""Sistema de eventos para tracking del flujo del agente."""

from dataclasses import dataclass, asdict
from typing import Any, Literal
from datetime import datetime
import json


@dataclass
class AgentEvent:
    """Evento del agente para streaming."""
    type: Literal["node_start", "node_end", "step", "tool_call", "tool_result", "error", "message"]
    node: str
    timestamp: str
    data: dict[str, Any]
    
    def to_json(self) -> str:
        """Convierte el evento a JSON."""
        return json.dumps(asdict(self), ensure_ascii=False)
    
    @staticmethod
    def node_start(node_name: str, input_data: Any = None) -> "AgentEvent":
        """Crea un evento de inicio de nodo."""
        return AgentEvent(
            type="node_start",
            node=node_name,
            timestamp=datetime.now().isoformat(),
            data={"input": str(input_data) if input_data else None}
        )
    
    @staticmethod
    def node_end(node_name: str, output_data: Any = None) -> "AgentEvent":
        """Crea un evento de fin de nodo."""
        return AgentEvent(
            type="node_end",
            node=node_name,
            timestamp=datetime.now().isoformat(),
            data={"output": str(output_data) if output_data else None}
        )
    
    @staticmethod
    def step(node_name: str, step_name: str, description: str, data: Any = None) -> "AgentEvent":
        """Crea un evento de paso intermedio."""
        return AgentEvent(
            type="step",
            node=node_name,
            timestamp=datetime.now().isoformat(),
            data={
                "step": step_name,
                "description": description,
                "data": data
            }
        )
    
    @staticmethod
    def tool_call(node_name: str, tool_name: str, arguments: dict) -> "AgentEvent":
        """Crea un evento de llamada a herramienta."""
        return AgentEvent(
            type="tool_call",
            node=node_name,
            timestamp=datetime.now().isoformat(),
            data={
                "tool": tool_name,
                "arguments": arguments
            }
        )
    
    @staticmethod
    def tool_result(node_name: str, tool_name: str, result: Any) -> "AgentEvent":
        """Crea un evento de resultado de herramienta."""
        return AgentEvent(
            type="tool_result",
            node=node_name,
            timestamp=datetime.now().isoformat(),
            data={
                "tool": tool_name,
                "result": str(result)
            }
        )
    
    @staticmethod
    def message(node_name: str, content: str, role: str = "assistant") -> "AgentEvent":
        """Crea un evento de mensaje."""
        return AgentEvent(
            type="message",
            node=node_name,
            timestamp=datetime.now().isoformat(),
            data={
                "role": role,
                "content": content
            }
        )
    
    @staticmethod
    def error(node_name: str, error_msg: str) -> "AgentEvent":
        """Crea un evento de error."""
        return AgentEvent(
            type="error",
            node=node_name,
            timestamp=datetime.now().isoformat(),
            data={"error": error_msg}
        )


class EventEmitter:
    """Emisor de eventos para streaming."""
    
    def __init__(self):
        self.events: list[AgentEvent] = []
        self.callbacks: list[callable] = []
    
    def emit(self, event: AgentEvent):
        """Emite un evento."""
        self.events.append(event)
        for callback in self.callbacks:
            callback(event)
    
    def on_event(self, callback: callable):
        """Registra un callback para eventos."""
        self.callbacks.append(callback)
    
    def clear(self):
        """Limpia los eventos."""
        self.events.clear()
