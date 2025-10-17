"""Router para endpoints de Assistants"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models import (
    Assistant,
    AssistantCreate,
    AssistantUpdate,
    AssistantSearch
)
from app.services import AssistantService

router = APIRouter(
    prefix="/assistants",
    tags=["Assistants"]
)


@router.post("", response_model=Assistant, status_code=200)
async def create_assistant(data: AssistantCreate):
    """
    Crea un nuevo assistant.
    
    Un assistant es una instancia configurada de un grafo (agente).
    """
    return AssistantService.create_assistant(data)


@router.post("/search", response_model=List[Assistant])
async def search_assistants(search: AssistantSearch):
    """
    Busca assistants según criterios específicos.
    """
    return AssistantService.search_assistants(search)


@router.get("", response_model=List[Assistant])
async def list_assistants(limit: int = 10, offset: int = 0):
    """
    Lista todos los assistants disponibles.
    """
    return AssistantService.list_assistants(limit, offset)


@router.get("/{assistant_id}", response_model=Assistant)
async def get_assistant(assistant_id: str):
    """
    Obtiene un assistant específico por ID.
    """
    return AssistantService.get_assistant(assistant_id)


@router.patch("/{assistant_id}", response_model=Assistant)
async def update_assistant(assistant_id: str, data: AssistantUpdate):
    """
    Actualiza un assistant existente.
    """
    return AssistantService.update_assistant(assistant_id, data)


@router.delete("/{assistant_id}")
async def delete_assistant(assistant_id: str):
    """
    Elimina un assistant.
    """
    return AssistantService.delete_assistant(assistant_id)


@router.post("/{assistant_id}/latest", response_model=Assistant)
async def set_latest_version(assistant_id: str, version: int):
    """
    Establece la versión activa de un assistant.
    """
    # Por ahora, simplemente actualizamos la versión
    return AssistantService.update_assistant(
        assistant_id,
        AssistantUpdate(version=str(version))
    )
