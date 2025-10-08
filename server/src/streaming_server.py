"""Servidor de streaming para el agente con visualización completa del flujo."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import AsyncGenerator
import json
import asyncio
from langchain_core.messages import HumanMessage

from agent.graph import graph
from agent.state import State


app = FastAPI(title="Agent Streaming Server", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    """Modelo para mensajes de chat."""
    content: str
    role: str = "human"


class StreamingRequest(BaseModel):
    """Modelo para requests de streaming."""
    message: ChatMessage
    thread_id: str | None = None


async def stream_agent_events(state: State) -> AsyncGenerator[str, None]:
    """Genera eventos del agente en tiempo real."""
    
    # Evento inicial
    yield f"data: {json.dumps({'type': 'start', 'data': 'Iniciando procesamiento...'})}\n\n"
    
    try:
        # Ejecutar el grafo y capturar eventos
        async for event in graph.astream(state, stream_mode="values"):
            # Enviar eventos del estado
            if "events" in event:
                for agent_event in event["events"]:
                    yield f"data: {json.dumps(agent_event)}\n\n"
                    await asyncio.sleep(0.1)  # Pequeña pausa para visualización
            
            # Enviar mensajes finales
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]
                if hasattr(last_message, 'content'):
                    yield f"data: {json.dumps({'type': 'final_message', 'content': last_message.content})}\n\n"
        
        # Evento de finalización
        yield f"data: {json.dumps({'type': 'end', 'data': 'Procesamiento completado'})}\n\n"
        
    except Exception as e:
        # Evento de error
        error_event = {
            'type': 'error',
            'data': str(e),
            'timestamp': '2024-01-01T00:00:00'
        }
        yield f"data: {json.dumps(error_event)}\n\n"


@app.post("/chat/stream")
async def stream_chat(request: StreamingRequest):
    """Endpoint de streaming para chat."""
    
    # Crear estado inicial
    state = State(
        messages=[HumanMessage(content=request.message.content)],
        events=[]
    )
    
    # Retornar respuesta de streaming
    return StreamingResponse(
        stream_agent_events(state),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@app.get("/health")
async def health_check():
    """Endpoint de salud."""
    return {"status": "healthy", "message": "Agent streaming server is running"}


@app.get("/")
async def root():
    """Endpoint raíz con información del servidor."""
    return {
        "name": "Agent Streaming Server",
        "version": "1.0.0",
        "description": "Servidor de streaming para agente multi-nodo con visualización completa",
        "endpoints": {
            "stream_chat": "/chat/stream",
            "health": "/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
