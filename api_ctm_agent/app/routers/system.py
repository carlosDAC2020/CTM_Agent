"""Router para endpoints del sistema"""

from fastapi import APIRouter
from app.services.database import db

router = APIRouter(
    tags=["System"]
)


@router.get("/ok")
async def health_check():
    """
    Health check del servidor.
    """
    return {"ok": True}


@router.get("/info")
async def get_info():
    """
    Información del servidor y estadísticas.
    """
    return {
        "version": "0.1.0",
        "name": "CTM Investment Agent API",
        "description": "API compatible con LangGraph para el agente de inversiones CTM",
        "stats": {
            "total_assistants": len(db.assistants),
            "total_threads": len(db.threads),
            "total_runs": len(db.runs)
        }
    }


@router.get("/")
async def root():
    """
    Endpoint raíz con información básica.
    """
    return {
        "message": "CTM Investment Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "playground": "/playground",
        "endpoints": {
            "assistants": "/assistants",
            "threads": "/threads",
            "runs": "/threads/{thread_id}/runs",
            "health": "/ok",
            "info": "/info"
        }
    }
