"""Almacenamiento en memoria (simulación de base de datos)"""

from typing import Dict, List, Any
from uuid import UUID
from app.models import Assistant, Thread, Run, Message

class InMemoryDatabase:
    """Base de datos en memoria para desarrollo"""
    
    def __init__(self):
        self.assistants: Dict[str, Dict] = {}
        self.threads: Dict[str, Dict] = {}
        self.runs: Dict[str, Dict] = {}
        self.messages: Dict[str, List[Message]] = {}
        self.thread_states: Dict[str, Dict] = {}
        
    def clear_all(self):
        """Limpiar toda la base de datos"""
        self.assistants.clear()
        self.threads.clear()
        self.runs.clear()
        self.messages.clear()
        self.thread_states.clear()


# Instancia global de la base de datos
db = InMemoryDatabase()
