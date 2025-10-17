"""
Ejemplo de uso de la API CTM Investment Agent
Demuestra el flujo completo de trabajo con la API
"""

import requests
import json
import time

# Configuración
API_BASE = "http://localhost:8000"

def print_section(title):
    """Imprime un separador visual"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def print_response(response):
    """Imprime una respuesta formateada"""
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()

def main():
    print_section("🚀 CTM Investment Agent API - Ejemplo de Uso")
    
    # 1. Verificar que el servidor esté funcionando
    print_section("1️⃣ Health Check")
    response = requests.get(f"{API_BASE}/ok")
    print_response(response)
    
    if response.status_code != 200:
        print("❌ El servidor no está disponible. Asegúrate de ejecutar 'python run.py' primero.")
        return
    
    # 2. Obtener información del servidor
    print_section("2️⃣ Información del Servidor")
    response = requests.get(f"{API_BASE}/info")
    print_response(response)
    
    # 3. Crear un Assistant
    print_section("3️⃣ Crear Assistant")
    assistant_data = {
        "graph_id": "agent",
        "name": "CTM Investment Agent - Demo",
        "metadata": {
            "version": "1.0",
            "purpose": "investment_analysis"
        }
    }
    
    response = requests.post(f"{API_BASE}/assistants", json=assistant_data)
    print_response(response)
    
    if response.status_code != 200:
        print("❌ Error creando assistant")
        return
    
    assistant_id = response.json()["assistant_id"]
    print(f"✅ Assistant creado con ID: {assistant_id}\n")
    
    # 4. Buscar assistants
    print_section("4️⃣ Buscar Assistants")
    search_data = {
        "graph_id": "agent",
        "limit": 5
    }
    
    response = requests.post(f"{API_BASE}/assistants/search", json=search_data)
    print_response(response)
    
    # 5. Crear un Thread
    print_section("5️⃣ Crear Thread")
    thread_data = {
        "metadata": {
            "user": "demo_user",
            "session": "example_session"
        }
    }
    
    response = requests.post(f"{API_BASE}/threads", json=thread_data)
    print_response(response)
    
    if response.status_code != 200:
        print("❌ Error creando thread")
        return
    
    thread_id = response.json()["thread_id"]
    print(f"✅ Thread creado con ID: {thread_id}\n")
    
    # 6. Ejecutar el agente (Run & Wait)
    print_section("6️⃣ Ejecutar Agente de Inversiones")
    run_data = {
        "assistant_id": assistant_id,
        "input": {
            "project_title": "Proyecto de Energía Solar en Colombia",
            "project_description": """
            Proyecto de instalación de paneles solares en zonas rurales de Colombia.
            
            Detalles:
            - Inversión estimada: $5,000,000 USD
            - Retorno esperado: 3-5 años
            - Beneficiarios: 10,000 familias
            - Ubicación: Departamentos de Cundinamarca y Boyacá
            - Tecnología: Paneles solares de última generación
            - Impacto ambiental: Reducción de 2,000 toneladas de CO2 anuales
            
            Buscamos identificar oportunidades de financiamiento y socios estratégicos.
            """,
            "messages": []
        },
        "metadata": {
            "run_type": "full_analysis"
        }
    }
    
    print("⏳ Ejecutando agente... (esto puede tomar unos segundos)\n")
    
    response = requests.post(
        f"{API_BASE}/threads/{thread_id}/runs/wait",
        json=run_data
    )
    print_response(response)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Run completado con éxito!")
        print(f"   Run ID: {result['run_id']}")
        print(f"   Status: {result['status']}\n")
    
    # 7. Obtener el estado del thread
    print_section("7️⃣ Estado del Thread")
    response = requests.get(f"{API_BASE}/threads/{thread_id}/state")
    print_response(response)
    
    # 8. Obtener mensajes del thread
    print_section("8️⃣ Historial de Mensajes")
    response = requests.get(f"{API_BASE}/threads/{thread_id}/messages")
    print_response(response)
    
    # 9. Listar runs del thread
    print_section("9️⃣ Listar Runs del Thread")
    response = requests.get(f"{API_BASE}/threads/{thread_id}/runs")
    print_response(response)
    
    # 10. Segunda interacción (continuación de la conversación)
    print_section("🔟 Segunda Interacción - Continuación")
    run_data_2 = {
        "assistant_id": assistant_id,
        "input": {
            "project_title": "Seguimiento",
            "project_description": "¿Cuáles son las mejores opciones de financiamiento para este proyecto?",
            "messages": []
        }
    }
    
    response = requests.post(
        f"{API_BASE}/threads/{thread_id}/runs/wait",
        json=run_data_2
    )
    print_response(response)
    
    # Resumen final
    print_section("📊 Resumen Final")
    print(f"✅ Assistant ID: {assistant_id}")
    print(f"✅ Thread ID: {thread_id}")
    print(f"✅ Total de runs ejecutados: 2")
    print(f"\n💡 Puedes continuar la conversación usando el mismo thread_id")
    print(f"💡 Visita el playground en: {API_BASE}/playground")
    print(f"💡 Documentación completa en: {API_BASE}/docs\n")
    
    print_section("🎉 Ejemplo Completado")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que el servidor esté ejecutándose con: python run.py")
    except KeyboardInterrupt:
        print("\n\n👋 Ejemplo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
