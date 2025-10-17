# test_agent.py (versión final corregida)

import httpx
import asyncio
import json
from typing import Dict, Any, List

# --- Configuración ---
LANGGRAPH_API_URL = "http://127.0.0.1:2024" 
ASSISTANT_ID = "agent"

# --- Módulo de Cliente API ---
class LangGraphClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def create_thread(self) -> str | None:
        async with httpx.AsyncClient() as client:
            try:
                print(f"   Conectando a {self.base_url}/threads...")
                response = await client.post(f"{self.base_url}/threads", json={}) 
                response.raise_for_status()
                print("   ✅ Conexión exitosa.")
                return response.json()["thread_id"]
            except httpx.ConnectError as e:
                print(f"❌ Error de conexión al crear el thread: {e}")
                print("   Asegúrate de que el servidor 'langgraph dev' está corriendo.")
                return None
            except httpx.RequestError as e:
                print(f"❌ Error en la petición al crear el thread: {e}")
                return None

    async def stream_run(self, thread_id: str, payload: Dict[str, Any]):
        url = f"{self.base_url}/threads/{thread_id}/runs/stream"
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    event_type = None
                    async for line in response.aiter_lines():
                        if line.startswith('event:'):
                            event_type = line.replace('event: ', '').strip()
                        elif line.startswith('data:'):
                            if not event_type: continue
                            try:
                                data_str = line[len('data: '):]
                                data = json.loads(data_str)
                                yield {"event": event_type, "data": data}
                                event_type = None 
                            except json.JSONDecodeError:
                                continue
        except httpx.HTTPStatusError as e:
            # Manejo de error mejorado para leer el cuerpo de la respuesta
            error_details = await e.response.aread()
            print(f"❌ Error en la API de LangGraph: {e.response.status_code}")
            print(f"   Detalles: {error_details.decode()}")
        except httpx.RequestError as e:
            print(f"❌ Error de conexión al hacer stream del run: {e}")

# --- Módulo de UI (sin cambios) ---
def display_opportunities(interrupt_data: Dict[str, Any]):
    print("\n" + "="*70)
    print("⚠️  ACCIÓN REQUERIDA: SELECCIÓN DE OPORTUNIDADES")
    print("="*70)
    opportunities = interrupt_data.get('opportunities', [])
    for opp in opportunities:
        print(f"\n  [{opp['index']}] {opp['origin']}")
        print(f"      📋 {opp.get('description', 'N/A')[:80]}...")
    print("\n" + "="*70)
    print(interrupt_data.get('instruction'))
    print("="*70)

def get_opportunity_selection(total_opportunities: int) -> List[int] | str:
    while True:
        user_input_str = input("\n👉 Tu selección (ej: 0,1 o 'all'): ")
        if user_input_str.lower().strip() == 'all':
            return 'all'
        try:
            indices = [int(i.strip()) for i in user_input_str.split(',')]
            if all(0 <= idx < total_opportunities for idx in indices):
                return indices
            else:
                print("❌ Uno o más índices están fuera de rango. Intenta de nuevo.")
        except ValueError:
            print("❌ Entrada inválida. Usa números separados por comas o 'all'.")

def display_chat_prompt(interrupt_data: Dict[str, Any]):
    print("\n" + "="*70)
    print("💬 MODO CHAT INTERACTIVO ACTIVADO")
    print("="*70)
    print(f"\n{interrupt_data.get('message', 'El reporte está listo.')}\n")
    if topics := interrupt_data.get('topics'):
        print("📚 Puedes preguntar sobre:")
        for topic in topics: print(f"   • {topic}")
    print("\n" + "="*70)
    print(interrupt_data.get('instruction', "Envía tu pregunta o 'end' para finalizar."))

# --- Lógica Principal (con el payload corregido) ---
async def main():
    print("🚀 Cliente Asíncrono para Agente CTM 🚀")
    client = LangGraphClient(LANGGRAPH_API_URL)

    print("1. Creando nuevo thread...")
    thread_id = await client.create_thread()
    if not thread_id: return
    print(f"   ✅ Thread creado: {thread_id}\n")

    print("2. Usando el proyecto de ejemplo 'AquaGuard AI'...")
    project_title = "AquaGuard AI: Sistema Predictivo de Monitoreo de Calidad del Agua con IoT y Detección de Patógenos"
    project_description = """El proyecto "AquaGuard AI" propone el desarrollo de una red de monitoreo de agua en tiempo real para la detección temprana de contaminantes y la predicción de eventos de riesgo para la salud pública. La solución está diseñada para ser desplegada en fuentes de agua críticas como ríos, embalses y lagos que abastecen a centros urbanos. La arquitectura se basa en boyas con sensores IoT, una plataforma en la nube y un motor de IA que utiliza redes neuronales recurrentes para análisis de series temporales y detección de anomalías. El objetivo es predecir la proliferación de algas nocivas y estimar la probabilidad de presencia de patógenos, permitiendo a las autoridades tomar medidas preventivas."""
    print(f"   - Título: {project_title}")
    print(f"   - Descripción: {project_description.strip()[:100]}...\n")
    
    # --- *** LA CORRECCIÓN ESTÁ AQUÍ *** ---
    payload = {
        "assistant_id": ASSISTANT_ID,
        "input": {
            "project_title": project_title,
            "project_description": project_description,
            "messages": [], # <-- AÑADIDO EL CAMPO OBLIGATORIO
        },
    }

    while True:
        print("\n--- ▶️  Ejecutando agente (esperando eventos en tiempo real) ---")
        interrupted = False
        async for event in client.stream_run(thread_id, payload):
            interrupted = True # Si recibimos CUALQUIER evento, sabemos que la ejecución no ha terminado
            if event["event"] == "values" and "messages" in event["data"]:
                last_message = event["data"]["messages"][-1]
                if isinstance(last_message, dict) and last_message.get('role') == 'assistant':
                    print(f"   🤖 Agente: {last_message['content']}")

            if event["event"] == "interrupt":
                interrupt_data = event["data"][0]["value"]
                if "opportunities" in interrupt_data:
                    display_opportunities(interrupt_data)
                    selection = get_opportunity_selection(interrupt_data.get("total_opportunities", 0))
                    payload = {"command": {"resume": selection}}
                    break
                elif "topics" in interrupt_data:
                    display_chat_prompt(interrupt_data)
                    question = input("\n💭 Tu pregunta: ")
                    if question.lower().strip() in ["end", "salir", "fin"]:
                        print("\n👋 Finalizando sesión.")
                        return
                    payload = {"command": {"resume": question}}
                    break
        
        if not interrupted:
            print("\n" + "="*70)
            print("✅ EJECUCIÓN DEL AGENTE COMPLETADA")
            print("="*70)
            break

if __name__ == "__main__":
    asyncio.run(main())