"""Modelos para Messages"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    """Modelo para crear un mensaje"""
    role: str = Field(..., description="Rol del mensaje: user, assistant, system")
    content: str = Field(..., description="Contenido del mensaje")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Message(BaseModel):
    """Modelo de Message completo"""
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Analiza este proyecto de inversión",
                "timestamp": "2025-10-16T11:27:00",
                "metadata": {}
            }
        }
