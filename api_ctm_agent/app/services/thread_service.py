"""Servicio para manejar Threads"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException
import httpx
import os

from app.models import Thread, ThreadCreate, ThreadUpdate, ThreadState, Message
from .database import db

# Configuración del servidor LangGraph
LANGGRAPH_API_URL = os.getenv("LANGGRAPH_API_URL", "http://127.0.0.1:2024")
USE_LANGGRAPH_SERVER = os.getenv("USE_LANGGRAPH_SERVER", "true").lower() == "true"


class ThreadService:
    """Servicio para operaciones CRUD de Threads"""
    
    @staticmethod
    async def create_thread(data: ThreadCreate) -> Thread:
        """Crea un nuevo thread"""
        # Si usamos el servidor de LangGraph, crear el thread allí
        if USE_LANGGRAPH_SERVER:
            return await ThreadService._create_thread_on_server(data)
        
        # Modo local
        thread_id = data.thread_id or str(uuid4())
        
        # Verificar si ya existe
        if thread_id in db.threads:
            if data.if_exists == "raise":
                raise HTTPException(status_code=409, detail="Thread ya existe")
            elif data.if_exists == "do_nothing":
                return Thread(**db.threads[thread_id])
        
        now = datetime.now()
        thread = Thread(
            thread_id=thread_id,
            created_at=now,
            updated_at=now,
            metadata=data.metadata,
            status="idle"
        )
        
        db.threads[thread_id] = thread.model_dump()
        db.messages[thread_id] = []
        db.thread_states[thread_id] = {
            "values": {},
            "next": [],
            "checkpoint": {},
            "metadata": data.metadata,
            "status": "idle",
            "interrupts": []
        }
        
        return thread
    
    @staticmethod
    def get_thread(thread_id: str) -> Thread:
        """Obtiene un thread por ID"""
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        return Thread(**db.threads[thread_id])
    
    @staticmethod
    def update_thread(thread_id: str, data: ThreadUpdate) -> Thread:
        """Actualiza un thread"""
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        thread_data = db.threads[thread_id]
        
        if data.metadata is not None:
            thread_data["metadata"].update(data.metadata)
        
        thread_data["updated_at"] = datetime.now()
        
        db.threads[thread_id] = thread_data
        return Thread(**thread_data)
    
    @staticmethod
    def delete_thread(thread_id: str) -> Dict[str, str]:
        """Elimina un thread"""
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        del db.threads[thread_id]
        if thread_id in db.messages:
            del db.messages[thread_id]
        if thread_id in db.thread_states:
            del db.thread_states[thread_id]
        
        return {"message": "Thread eliminado exitosamente"}
    
    @staticmethod
    async def list_threads(limit: int = 10, offset: int = 0) -> List[Thread]:
        """Lista todos los threads"""
        # Si usamos el servidor de LangGraph, obtener threads de allí
        if USE_LANGGRAPH_SERVER:
            return await ThreadService._list_threads_from_server(limit, offset)
        
        # Modo local
        all_threads = [
            Thread(**data) for data in db.threads.values()
        ]
        all_threads.sort(key=lambda x: x.created_at, reverse=True)
        return all_threads[offset:offset + limit]
    
    @staticmethod
    async def get_thread_state(thread_id: str) -> ThreadState:
        """Obtiene el estado actual del thread"""
        # Si usamos el servidor de LangGraph, obtener estado de allí
        if USE_LANGGRAPH_SERVER:
            return await ThreadService._get_thread_state_from_server(thread_id)
        
        # Modo local
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        if thread_id not in db.thread_states:
            db.thread_states[thread_id] = {
                "values": {},
                "next": [],
                "checkpoint": {},
                "metadata": {},
                "status": "idle",
                "interrupts": []
            }
        
        state_data = db.thread_states[thread_id]
        
        # Incluir mensajes en el estado
        if thread_id in db.messages:
            state_data["values"]["messages"] = [
                msg.model_dump() if isinstance(msg, Message) else msg
                for msg in db.messages[thread_id]
            ]
        
        return ThreadState(**state_data)
    
    @staticmethod
    def update_thread_state(
        thread_id: str, 
        values: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        interrupts: Optional[List[Dict[str, Any]]] = None
    ):
        """Actualiza el estado del thread"""
        if thread_id not in db.thread_states:
            db.thread_states[thread_id] = {
                "values": {},
                "next": [],
                "checkpoint": {},
                "metadata": {},
                "status": "idle",
                "interrupts": []
            }
        
        if values is not None:
            db.thread_states[thread_id]["values"].update(values)
        
        if status is not None:
            db.thread_states[thread_id]["status"] = status
            db.threads[thread_id]["status"] = status
        
        if interrupts is not None:
            db.thread_states[thread_id]["interrupts"] = interrupts
    
    @staticmethod
    def add_message(thread_id: str, message: Message):
        """Agrega un mensaje al thread"""
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        if thread_id not in db.messages:
            db.messages[thread_id] = []
        
        db.messages[thread_id].append(message)
    
    @staticmethod
    def get_messages(thread_id: str) -> List[Message]:
        """Obtiene todos los mensajes de un thread"""
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        return db.messages.get(thread_id, [])
    
    # ========== MÉTODOS PARA SERVIDOR DE LANGGRAPH ==========
    
    @staticmethod
    async def _create_thread_on_server(data: ThreadCreate) -> Thread:
        """Crea un thread en el servidor de LangGraph"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "metadata": data.metadata or {}
                }
                if data.thread_id:
                    payload["thread_id"] = data.thread_id
                
                response = await client.post(
                    f"{LANGGRAPH_API_URL}/threads",
                    json=payload
                )
                
                if response.status_code == 200:
                    thread_data = response.json()
                    return Thread(
                        thread_id=thread_data["thread_id"],
                        created_at=datetime.fromisoformat(thread_data["created_at"].replace("Z", "+00:00")),
                        updated_at=datetime.fromisoformat(thread_data["updated_at"].replace("Z", "+00:00")),
                        metadata=thread_data.get("metadata", {}),
                        status=thread_data.get("status", "idle")
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error creando thread en LangGraph Server: {response.text}"
                    )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error conectando con LangGraph Server: {str(e)}")
    
    @staticmethod
    async def _list_threads_from_server(limit: int = 10, offset: int = 0) -> List[Thread]:
        """Lista threads desde el servidor de LangGraph"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # LangGraph usa POST /threads/search en lugar de GET /threads
                response = await client.post(
                    f"{LANGGRAPH_API_URL}/threads/search",
                    json={"limit": limit, "offset": offset}
                )
                
                if response.status_code == 200:
                    threads_data = response.json()
                    threads = []
                    for thread_data in threads_data:
                        threads.append(Thread(
                            thread_id=thread_data["thread_id"],
                            created_at=datetime.fromisoformat(thread_data["created_at"].replace("Z", "+00:00")),
                            updated_at=datetime.fromisoformat(thread_data["updated_at"].replace("Z", "+00:00")),
                            metadata=thread_data.get("metadata", {}),
                            status=thread_data.get("status", "idle")
                        ))
                    return threads
                else:
                    print(f"⚠️ Error listando threads: {response.status_code}")
                    return []
        except httpx.HTTPError as e:
            print(f"⚠️ Error conectando con LangGraph Server: {e}")
            return []
    
    @staticmethod
    async def _get_thread_state_from_server(thread_id: str) -> ThreadState:
        """Obtiene el estado detallado del thread desde el servidor de LangGraph"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{LANGGRAPH_API_URL}/threads/{thread_id}/state"
                )
                
                if response.status_code == 200:
                    state_data = response.json()
                    
                    # Parsear el estado de LangGraph
                    return ThreadState(
                        values=state_data.get("values", {}),
                        next=state_data.get("next", []),
                        checkpoint=state_data.get("checkpoint", {}),
                        metadata=state_data.get("metadata", {}),
                        created_at=datetime.fromisoformat(state_data["created_at"].replace("Z", "+00:00")) if "created_at" in state_data else None,
                        parent_checkpoint=state_data.get("parent_checkpoint"),
                        interrupts=state_data.get("tasks", []),  # LangGraph usa 'tasks' para interrupciones
                        status="interrupted" if state_data.get("tasks") else "idle"
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error obteniendo estado del thread: {response.text}"
                    )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error conectando con LangGraph Server: {str(e)}")
