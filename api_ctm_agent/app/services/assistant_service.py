"""Servicio para manejar Assistants"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException

from app.models import Assistant, AssistantCreate, AssistantUpdate, AssistantSearch
from .database import db


class AssistantService:
    """Servicio para operaciones CRUD de Assistants"""
    
    @staticmethod
    def create_assistant(data: AssistantCreate) -> Assistant:
        """Crea un nuevo assistant"""
        assistant_id = str(uuid4())
        
        # Verificar si ya existe
        if data.if_exists == "raise":
            existing = AssistantService.search_assistants(
                AssistantSearch(graph_id=data.graph_id, limit=1)
            )
            if existing:
                raise HTTPException(status_code=409, detail="Assistant ya existe")
        
        now = datetime.now()
        assistant = Assistant(
            assistant_id=assistant_id,
            graph_id=data.graph_id,
            name=data.name or f"Assistant-{assistant_id[:8]}",
            metadata=data.metadata,
            config=data.config,
            created_at=now,
            updated_at=now,
            version=1
        )
        
        db.assistants[assistant_id] = assistant.model_dump()
        return assistant
    
    @staticmethod
    def get_assistant(assistant_id: str) -> Assistant:
        """Obtiene un assistant por ID"""
        if assistant_id not in db.assistants:
            raise HTTPException(status_code=404, detail="Assistant no encontrado")
        
        return Assistant(**db.assistants[assistant_id])
    
    @staticmethod
    def update_assistant(assistant_id: str, data: AssistantUpdate) -> Assistant:
        """Actualiza un assistant"""
        if assistant_id not in db.assistants:
            raise HTTPException(status_code=404, detail="Assistant no encontrado")
        
        assistant_data = db.assistants[assistant_id]
        
        if data.name is not None:
            assistant_data["name"] = data.name
        if data.metadata is not None:
            assistant_data["metadata"].update(data.metadata)
        if data.config is not None:
            assistant_data["config"].update(data.config)
        if data.version is not None:
            assistant_data["version"] = data.version
        
        assistant_data["updated_at"] = datetime.now()
        
        db.assistants[assistant_id] = assistant_data
        return Assistant(**assistant_data)
    
    @staticmethod
    def delete_assistant(assistant_id: str) -> Dict[str, str]:
        """Elimina un assistant"""
        if assistant_id not in db.assistants:
            raise HTTPException(status_code=404, detail="Assistant no encontrado")
        
        del db.assistants[assistant_id]
        return {"message": "Assistant eliminado exitosamente"}
    
    @staticmethod
    def search_assistants(search: AssistantSearch) -> List[Assistant]:
        """Busca assistants según criterios"""
        results = []
        
        for assistant_data in db.assistants.values():
            # Filtrar por graph_id si se especifica
            if search.graph_id and assistant_data["graph_id"] != search.graph_id:
                continue
            
            # Filtrar por metadata si se especifica
            if search.metadata:
                match = all(
                    assistant_data["metadata"].get(k) == v
                    for k, v in search.metadata.items()
                )
                if not match:
                    continue
            
            results.append(Assistant(**assistant_data))
        
        # Ordenar por fecha de creación (más recientes primero)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Aplicar paginación
        return results[search.offset:search.offset + search.limit]
    
    @staticmethod
    def list_assistants(limit: int = 10, offset: int = 0) -> List[Assistant]:
        """Lista todos los assistants"""
        all_assistants = [
            Assistant(**data) for data in db.assistants.values()
        ]
        all_assistants.sort(key=lambda x: x.created_at, reverse=True)
        return all_assistants[offset:offset + limit]
