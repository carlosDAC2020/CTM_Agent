"""Modelos para Assistants"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class AssistantCreate(BaseModel):
    """Modelo para crear un assistant"""
    graph_id: str = Field(..., description="ID del grafo a usar")
    name: Optional[str] = Field(None, description="Nombre del assistant")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    if_exists: Optional[str] = Field("do_nothing", description="Acción si ya existe: do_nothing, update, raise")


class AssistantUpdate(BaseModel):
    """Modelo para actualizar un assistant"""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    version: Optional[str] = None


class AssistantVersion(BaseModel):
    """Versión de un assistant"""
    version: int
    config: Dict[str, Any]
    created_at: datetime
    

class Assistant(BaseModel):
    """Modelo de Assistant completo"""
    assistant_id: str
    graph_id: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    version: int = 1


class AssistantSearch(BaseModel):
    """Modelo para buscar assistants"""
    graph_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    limit: int = 10
    offset: int = 0
