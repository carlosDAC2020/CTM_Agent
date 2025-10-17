from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4, UUID
import uvicorn

app = FastAPI(
    title="LangGraph Agent Playground",
    description="Simple playground para manejar agentes con API similar a LangGraph",
    version="0.1.0"
)

# CORS para permitir requests desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= MODELOS =============

class ThreadCreate(BaseModel):
    thread_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = {}

class Thread(BaseModel):
    thread_id: UUID
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    status: str = "idle"

class RunCreate(BaseModel):
    assistant_id: str = "agent"
    input: Any
    metadata: Optional[Dict[str, Any]] = {}
    stream_mode: List[str] = ["values"]

class Run(BaseModel):
    run_id: UUID
    thread_id: UUID
    assistant_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

# ============= ALMACENAMIENTO TEMPORAL =============
# En producción usarías una base de datos real

threads_db: Dict[UUID, Dict] = {}
runs_db: Dict[UUID, Dict] = {}
messages_db: Dict[UUID, List[Message]] = {}

# ============= TU AGENTE =============
# Aquí integrarías tu agente real

class AgentHandler:
    """
    Clase para manejar tu agente.
    Reemplaza esto con tu implementación real.
    """
    
    @staticmethod
    async def process_input(user_input: Any, thread_id: UUID) -> str:
        """
        Procesa el input del usuario y devuelve la respuesta del agente.
        
        REEMPLAZA ESTA FUNCIÓN CON TU AGENTE REAL
        """
        # Ejemplo simple - reemplazar con tu agente
        if isinstance(user_input, dict):
            user_message = user_input.get("messages", [{"content": ""}])[-1].get("content", "")
        else:
            user_message = str(user_input)
        
        # Aquí llamarías a tu agente real
        # response = tu_agente.invoke(user_message)
        
        # Respuesta de ejemplo
        response = f"[AGENTE] Recibí tu mensaje: '{user_message}'. Respuesta simulada."
        
        return response

agent = AgentHandler()

# ============= ENDPOINTS =============

@app.get("/")
async def root():
    return {
        "message": "LangGraph Agent Playground",
        "docs": "/docs",
        "endpoints": {
            "threads": "/threads",
            "runs": "/threads/{thread_id}/runs"
        }
    }

# --- THREADS ---

@app.post("/threads", response_model=Thread)
async def create_thread(thread_data: ThreadCreate):
    """Crear un nuevo thread (conversación)"""
    thread_id = thread_data.thread_id or uuid4()
    
    if thread_id in threads_db:
        raise HTTPException(status_code=409, detail="Thread ya existe")
    
    now = datetime.now()
    thread = {
        "thread_id": thread_id,
        "created_at": now,
        "updated_at": now,
        "metadata": thread_data.metadata,
        "status": "idle"
    }
    
    threads_db[thread_id] = thread
    messages_db[thread_id] = []
    
    return thread

@app.get("/threads/{thread_id}", response_model=Thread)
async def get_thread(thread_id: UUID):
    """Obtener información de un thread"""
    if thread_id not in threads_db:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    return threads_db[thread_id]

@app.get("/threads", response_model=List[Thread])
async def list_threads(limit: int = 10, offset: int = 0):
    """Listar todos los threads"""
    all_threads = list(threads_db.values())
    return all_threads[offset:offset + limit]

@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: UUID):
    """Eliminar un thread"""
    if thread_id not in threads_db:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    del threads_db[thread_id]
    if thread_id in messages_db:
        del messages_db[thread_id]
    
    return {"message": "Thread eliminado"}

# --- RUNS (Ejecuciones) ---

@app.post("/threads/{thread_id}/runs/wait")
async def create_run_and_wait(thread_id: UUID, run_data: RunCreate):
    """
    Crear una ejecución en el thread y esperar la respuesta.
    Este es el endpoint principal para interactuar con el agente.
    """
    if thread_id not in threads_db:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    # Crear run
    run_id = uuid4()
    now = datetime.now()
    
    run = {
        "run_id": run_id,
        "thread_id": thread_id,
        "assistant_id": run_data.assistant_id,
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "metadata": run_data.metadata
    }
    
    runs_db[run_id] = run
    threads_db[thread_id]["status"] = "busy"
    
    try:
        # Guardar mensaje del usuario
        if isinstance(run_data.input, dict) and "messages" in run_data.input:
            user_content = run_data.input["messages"][-1].get("content", "")
        else:
            user_content = str(run_data.input)
        
        user_msg = Message(role="user", content=user_content)
        messages_db[thread_id].append(user_msg)
        
        # Procesar con el agente
        agent_response = await agent.process_input(run_data.input, thread_id)
        
        # Guardar respuesta del agente
        agent_msg = Message(role="assistant", content=agent_response)
        messages_db[thread_id].append(agent_msg)
        
        # Actualizar run
        run["status"] = "success"
        run["updated_at"] = datetime.now()
        threads_db[thread_id]["status"] = "idle"
        
        return {
            "run_id": run_id,
            "thread_id": thread_id,
            "status": "success",
            "output": {
                "messages": [
                    {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
                    for msg in messages_db[thread_id]
                ]
            }
        }
        
    except Exception as e:
        run["status"] = "error"
        threads_db[thread_id]["status"] = "error"
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threads/{thread_id}/runs")
async def list_runs(thread_id: UUID, limit: int = 10, offset: int = 0):
    """Listar ejecuciones de un thread"""
    if thread_id not in threads_db:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    thread_runs = [r for r in runs_db.values() if r["thread_id"] == thread_id]
    return thread_runs[offset:offset + limit]

@app.get("/threads/{thread_id}/messages")
async def get_messages(thread_id: UUID):
    """Obtener historial de mensajes de un thread"""
    if thread_id not in threads_db:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    return {
        "thread_id": thread_id,
        "messages": [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
            for msg in messages_db.get(thread_id, [])
        ]
    }

# --- ESTADO DEL THREAD ---

@app.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: UUID):
    """Obtener el estado actual del thread"""
    if thread_id not in threads_db:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    return {
        "values": {
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages_db.get(thread_id, [])
            ]
        },
        "next": [],
        "checkpoint": {},
        "metadata": threads_db[thread_id]["metadata"]
    }

# --- INFO DEL SISTEMA ---

@app.get("/info")
async def get_info():
    """Información del servidor"""
    return {
        "version": "0.1.0",
        "agent_type": "custom",
        "total_threads": len(threads_db),
        "total_runs": len(runs_db)
    }

@app.get("/ok")
async def health_check():
    """Health check"""
    return {"ok": True}

# ============= EJECUTAR =============

if __name__ == "__main__":
    print("🚀 Iniciando LangGraph Agent Playground...")
    print("📝 Documentación: http://localhost:8000/docs")
    print("🔧 API: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)