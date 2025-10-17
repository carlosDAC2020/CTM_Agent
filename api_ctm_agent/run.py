"""Script para ejecutar el servidor de la API"""

import uvicorn
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Iniciando CTM Investment Agent API Server")
    print("=" * 70)
    print()
    print("📝 Documentación interactiva: http://localhost:8000/docs")
    print("🎮 Playground: http://localhost:8000/playground")
    print("📊 ReDoc: http://localhost:8000/redoc")
    print("🔧 Info del servidor: http://localhost:8000/info")
    print()
    print("=" * 70)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
