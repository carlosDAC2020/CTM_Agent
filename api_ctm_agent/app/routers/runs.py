"""Router para endpoints de Runs"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models import (
    Run,
    RunCreate,
    RunOutput
)
from app.services import RunService

router = APIRouter(
    prefix="/threads/{thread_id}/runs",
    tags=["Thread Runs"]
)


@router.post("", response_model=Run, status_code=200)
async def create_run(thread_id: str, data: RunCreate):
    """
    Crea una nueva ejecución en el thread.
    
    Un run es una invocación del grafo/assistant en un thread.
    Actualiza el estado del thread.
    """
    return await RunService.create_run(thread_id, data)


@router.post("/wait", response_model=RunOutput)
async def create_run_and_wait(thread_id: str, data: RunCreate):
    """
    Crea una ejecución y espera a que se complete.
    
    Este es el endpoint principal para interactuar con el agente de forma síncrona.
    """
    # Crear el run
    run = await RunService.create_run(thread_id, data)
    
    # Ejecutar y esperar resultado
    result = await RunService.execute_run(thread_id, run.run_id, data)
    
    return result


@router.get("", response_model=List[Run])
async def list_runs(thread_id: str, limit: int = 10, offset: int = 0):
    """
    Lista todas las ejecuciones de un thread.
    """
    return RunService.list_runs(thread_id, limit, offset)


@router.get("/{run_id}", response_model=Run)
async def get_run(thread_id: str, run_id: str):
    """
    Obtiene una ejecución específica por ID.
    """
    return RunService.get_run(thread_id, run_id)


@router.post("/{run_id}/cancel", response_model=Run)
async def cancel_run(thread_id: str, run_id: str):
    """
    Cancela una ejecución en progreso.
    """
    return RunService.cancel_run(thread_id, run_id)


@router.post("/stream")
async def create_run_stream(thread_id: str, data: RunCreate):
    """
    Crea una ejecución con streaming de eventos.
    
    Nota: Esta es una implementación simplificada.
    Para streaming real, se necesitaría SSE o WebSockets.
    """
    # Por ahora, retornamos el resultado completo
    run = await RunService.create_run(thread_id, data)
    result = await RunService.execute_run(thread_id, run.run_id, data)
    
    return {
        "run_id": run.run_id,
        "events": [
            {"type": "start", "data": run.model_dump()},
            {"type": "end", "data": result.model_dump()}
        ]
    }
