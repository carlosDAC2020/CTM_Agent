"""Aplicación principal FastAPI"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from app.routers import (
    assistants_router,
    threads_router,
    runs_router,
    system_router
)

# Crear la aplicación
app = FastAPI(
    title="CTM Investment Agent API",
    description="API compatible con LangGraph para el agente de análisis de inversiones CTM",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(system_router)
app.include_router(assistants_router)
app.include_router(threads_router)
app.include_router(runs_router)

# Servir archivos estáticos para el playground
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/playground", response_class=HTMLResponse)
async def playground():
    """
    Playground interactivo para probar el agente
    """
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "playground.html")
    
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        <html>
            <head><title>Playground</title></head>
            <body>
                <h1>Playground no disponible</h1>
                <p>El archivo de template no se encontró.</p>
                <p>Usa <a href="/docs">/docs</a> para explorar la API.</p>
            </body>
        </html>
        """


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    print("=" * 60)
    print("🚀 CTM Investment Agent API iniciada")
    print("=" * 60)
    print("📝 Documentación: http://localhost:8000/docs")
    print("🎮 Playground: http://localhost:8000/playground")
    print("🔧 API Info: http://localhost:8000/info")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    print("\n👋 Cerrando CTM Investment Agent API...")
