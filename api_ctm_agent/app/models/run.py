"""Modelos para Runs"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from uuid import UUID
from enum import Enum


class StreamMode(str, Enum):
    """Modos de streaming"""
    VALUES = "values"
    MESSAGES = "messages"
    UPDATES = "updates"
    EVENTS = "events"
    DEBUG = "debug"


class RunStatus(str, Enum):
    """Estados de un run"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"


class RunCreate(BaseModel):
    """Modelo para crear un run"""
    assistant_id: str
    input: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    stream_mode: List[StreamMode] = Field(default=[StreamMode.VALUES])
    interrupt_before: Optional[List[str]] = None
    interrupt_after: Optional[List[str]] = None
    webhook: Optional[str] = None
    multitask_strategy: Optional[str] = None
    command: Optional[Literal["resume", "update"]] = None


class Run(BaseModel):
    """Modelo de Run completo"""
    run_id: str
    thread_id: str
    assistant_id: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    multitask_strategy: Optional[str] = None
    

class RunOutput(BaseModel):
    """Output de un run"""
    run_id: str
    thread_id: str
    status: RunStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
