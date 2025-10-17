"""Modelos comunes compartidos"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class Metadata(BaseModel):
    """Metadata genérica"""
    data: Dict[str, Any] = Field(default_factory=dict)


class Config(BaseModel):
    """Configuración para runs y assistants"""
    configurable: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[list[str]] = Field(default_factory=list)
    recursion_limit: Optional[int] = 25
    max_concurrency: Optional[int] = None


class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""
    detail: str
    status_code: int = 500
    timestamp: datetime = Field(default_factory=datetime.now)
