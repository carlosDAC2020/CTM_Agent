"""Script para iniciar el servidor de chat con visualización completa."""

import uvicorn
import webbrowser
import os
import time
from pathlib import Path

def start_server():
    """Inicia el servidor de streaming y abre la interfaz de chat."""
    
    print("🚀 Iniciando Servidor de Chat con Visualización Completa")
    print("=" * 60)
    
    # Ruta del servidor
    server_path = Path(__file__).parent / "server" / "src"
    os.chdir(server_path)
    
    print(f"📁 Directorio de trabajo: {server_path}")
    print("🔧 Configurando servidor...")
    
    # Configuración del servidor
    config = uvicorn.Config(
        "streaming_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
    print("🌐 Servidor configurado:")
    print(f"   • URL: http://localhost:8000")
    print(f"   • Docs: http://localhost:8000/docs")
    print(f"   • Health: http://localhost:8000/health")
    
    # Abrir interfaz de chat en el navegador
    chat_interface_path = Path(__file__).parent / "chat_interface.html"
    print(f"💬 Abriendo interfaz de chat: {chat_interface_path}")
    
    # Iniciar servidor en un hilo separado
    server = uvicorn.Server(config)
    
    try:
        print("\n🎯 Iniciando servidor...")
        print("   Presiona Ctrl+C para detener")
        print("=" * 60)
        
        # Abrir navegador después de un breve delay
        import threading
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"file://{chat_interface_path.absolute()}")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Iniciar servidor
        server.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo servidor...")
        print("¡Gracias por usar el Chat Agent!")

if __name__ == "__main__":
    start_server()
