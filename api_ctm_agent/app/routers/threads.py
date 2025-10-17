"""Router para endpoints de Threads"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.models import (
    Thread,
    ThreadCreate,
    ThreadUpdate,
    ThreadState,
    Message
)
from app.services import ThreadService

router = APIRouter(
    prefix="/threads",
    tags=["Threads"]
)


@router.post("", response_model=Thread, status_code=200)
async def create_thread(data: ThreadCreate):
    """
    Crea un nuevo thread (conversación).
    
    Un thread contiene el estado acumulado de un grupo de ejecuciones.
    """
    return await ThreadService.create_thread(data)


@router.get("", response_model=List[Thread])
async def list_threads(limit: int = 10, offset: int = 0):
    """
    Lista todos los threads disponibles.
    """
    return await ThreadService.list_threads(limit, offset)


@router.get("/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str):
    """
    Obtiene un thread específico por ID.
    """
    return ThreadService.get_thread(thread_id)


@router.patch("/{thread_id}", response_model=Thread)
async def update_thread(thread_id: str, data: ThreadUpdate):
    """
    Actualiza un thread existente.
    """
    return ThreadService.update_thread(thread_id, data)


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str):
    """
    Elimina un thread y todo su contenido.
    """
    return ThreadService.delete_thread(thread_id)


@router.get("/{thread_id}/state", response_model=ThreadState)
async def get_thread_state(thread_id: str):
    """
    Obtiene el estado actual del thread.
    
    Incluye valores, checkpoints, metadata e interrupciones.
    """
    return await ThreadService.get_thread_state(thread_id)


@router.get("/{thread_id}/messages")
async def get_thread_messages(thread_id: str):
    """
    Obtiene el historial de mensajes de un thread.
    """
    messages = ThreadService.get_messages(thread_id)
    return {
        "thread_id": thread_id,
        "messages": [
            msg.model_dump() if isinstance(msg, Message) else msg
            for msg in messages
        ]
    }


@router.post("/{thread_id}/state/checkpoint")
async def create_checkpoint(thread_id: str):
    """
    Crea un checkpoint del estado actual del thread.
    """
    state = await ThreadService.get_thread_state(thread_id)
    return {
        "thread_id": thread_id,
        "checkpoint": state.checkpoint,
        "message": "Checkpoint creado"
    }


@router.get("/{thread_id}/inspect")
async def inspect_thread(thread_id: str):
    """
    Inspecciona el estado detallado del thread para debugging.
    
    Retorna información sobre:
    - Nodo actual
    - Interrupciones pendientes
    - Tipo de interrupción (selección de oportunidades, chat, etc.)
    - Valores del estado (ProjectState)
    - Historial de ejecución
    """
    state = await ThreadService.get_thread_state(thread_id)
    thread = ThreadService.get_thread(thread_id)
    
    # Analizar el estado para determinar qué está pasando
    inspection = {
        "thread_id": thread_id,
        "status": state.status,
        "current_node": None,
        "next_nodes": state.next,
        "is_interrupted": len(state.interrupts) > 0 if state.interrupts else False,
        "interruption_type": None,
        "interruption_details": None,
        "state_values": state.values,
        "metadata": thread.metadata,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at
    }
    
    # Determinar el nodo actual desde el checkpoint
    if state.checkpoint and "channel_values" in state.checkpoint:
        # El último nodo ejecutado
        inspection["current_node"] = state.checkpoint.get("channel_values", {}).get("__pregel_resuming", "unknown")
    
    # Analizar interrupciones
    if state.interrupts and len(state.interrupts) > 0:
        first_interrupt = state.interrupts[0]
        
        # Determinar el tipo de interrupción
        if isinstance(first_interrupt, dict):
            # Interrupción de selección de oportunidades
            if "total_opportunities" in first_interrupt or "opportunities" in first_interrupt:
                inspection["interruption_type"] = "opportunity_selection"
                inspection["interruption_details"] = {
                    "message": "Esperando selección de oportunidades",
                    "opportunities": first_interrupt.get("opportunities", []),
                    "total": first_interrupt.get("total_opportunities", 0),
                    "instruction": first_interrupt.get("instruction", "Selecciona las oportunidades")
                }
            # Interrupción de chat
            elif "topics" in first_interrupt or "message" in first_interrupt:
                inspection["interruption_type"] = "chat_interaction"
                inspection["interruption_details"] = {
                    "message": first_interrupt.get("message", "Modo chat activo"),
                    "topics": first_interrupt.get("topics", []),
                    "instruction": first_interrupt.get("instruction", "Haz una pregunta")
                }
            else:
                inspection["interruption_type"] = "custom"
                inspection["interruption_details"] = first_interrupt
    
    # Información del ProjectState
    if "project_title" in state.values:
        inspection["project_info"] = {
            "title": state.values.get("project_title"),
            "description": state.values.get("project_description", "")[:200] + "...",
            "has_opportunities": "investment_opportunities" in state.values,
            "opportunities_count": len(state.values.get("investment_opportunities", [])),
            "selected_count": len(state.values.get("selected_opportunities", [])),
            "has_report": bool(state.values.get("final_report"))
        }
    
    return inspection
