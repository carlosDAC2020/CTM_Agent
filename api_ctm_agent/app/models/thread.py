"""Modelos para Threads"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class ThreadCreate(BaseModel):
    """Modelo para crear un thread"""
    thread_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    if_exists: Optional[str] = Field("do_nothing", description="Acción si ya existe")


class ThreadUpdate(BaseModel):
    """Modelo para actualizar un thread"""
    metadata: Optional[Dict[str, Any]] = None


class Thread(BaseModel):
    """Modelo de Thread completo"""
    thread_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = "idle"


class ThreadState(BaseModel):
    """Estado de un thread"""
    values: Dict[str, Any] = Field(default_factory=dict)
    next: List[str] = Field(default_factory=list)
    checkpoint: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    parent_checkpoint: Optional[Dict[str, Any]] = None
    interrupts: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    status: str = "idle"
