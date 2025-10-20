import os
import sys
import json
import requests
from typing import Optional, Dict, Any

# Configuración base
BASE_URL = "http://127.0.0.1:2024"
ASSISTANT_ID = "agent"  # ID del agente LangGraph

class AgentTester:
    def __init__(self):
        self.thread_id: Optional[str] = None
        self.base_url = os.getenv("LANGGRAPH_URL", BASE_URL)
        self.assistant_id = os.getenv("ASSISTANT_ID", ASSISTANT_ID)

    def clear_screen(self):
        """Limpia la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        """Muestra un encabezado en la consola."""
        self.clear_screen()
        print("=" * 50)
        print(f"{title:^50}")
        print("=" * 50)

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una petición HTTP al servidor LangGraph."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Error en la petición: {e}")
            return {}

    def create_thread(self):
        """Crea un nuevo hilo de conversación."""
        self.print_header("CREAR NUEVO HILO")
        result = self.make_request("POST", "threads", json={})
        if result and "thread_id" in result:
            self.thread_id = result["thread_id"]
            print(f"✅ Hilo creado con éxito!")
            print(f"ID del Hilo: {self.thread_id}")
        else:
            print("❌ No se pudo crear el hilo. Verifica que el servidor esté en ejecución.")
        input("\nPresiona Enter para continuar...")

    def run_agent(self):
        """Ejecuta el agente en el hilo actual."""
        if not self.thread_id:
            print("❌ No hay un hilo activo. Crea uno primero.")
            input("\nPresiona Enter para continuar...")
            return

        self.print_header(f"EJECUTANDO AGENTE - Hilo: {self.thread_id}")
        
        # Datos iniciales para el agente
        project_title = input("Título del proyecto: ")
        project_description = input("Descripción del proyecto: ")
        
        payload = {
            "assistant_id": self.assistant_id,
            "input": {
                "project_title": project_title,
                "project_description": project_description
            }
        }
        
        self._stream_agent_response(payload)

    def _stream_agent_response(self, payload: Dict[str, Any]):
        """Maneja la respuesta en streaming del agente."""
        url = f"{self.base_url}/threads/{self.thread_id}/runs/stream"
        
        try:
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()
                
                print("\n--- [RESPUESTA DEL AGENTE] ---")
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            # Aquí puedes procesar la respuesta del agente
                            if "messages" in data and data["messages"]:
                                for msg in data["messages"]:
                                    if msg.get("role") == "assistant":
                                        print(f"🤖 {msg.get('content', '')}")
                            
                            # Manejo de interrupciones
                            if "interrupts" in data and data["interrupts"]:
                                self._handle_interrupts(data["interrupts"])
                                
                        except json.JSONDecodeError:
                            continue
                
                print("\n--- [FIN DE LA RESPUESTA] ---")
                
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Error en la comunicación con el agente: {e}")
        
        input("\nPresiona Enter para continuar...")

    def _handle_interrupts(self, interrupts: list):
        """Maneja las interrupciones del agente."""
        print("\n⚠️  [INTERRUPCIÓN] El agente requiere tu atención:")
        
        for i, interrupt in enumerate(interrupts, 1):
            print(f"\n{i}. {interrupt.get('type', 'Interrupción no especificada')}")
            print(f"   Detalles: {interrupt.get('details', 'Sin detalles adicionales')}")
            
            # Aquí puedes manejar diferentes tipos de interrupciones
            if "opportunities" in interrupt:
                self._handle_opportunities(interrupt["opportunities"])
        
        # Solicitar entrada del usuario
        user_input = input("\n🔹 Ingresa tu respuesta: ")
        
        # Continuar la ejecución con la entrada del usuario
        continue_payload = {
            "assistant_id": self.assistant_id,
            "command": {"resume": user_input}
        }
        self._stream_agent_response(continue_payload)

    def _handle_opportunities(self, opportunities: list):
        """Maneja las oportunidades de inversión."""
        print("\nOportunidades encontradas:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp.get('title', 'Sin título')}")
            print(f"     {opp.get('description', 'Sin descripción')}")

    def view_thread_state(self):
        """Muestra el estado actual del hilo."""
        if not self.thread_id:
            print("❌ No hay un hilo activo. Crea uno primero.")
            input("\nPresiona Enter para continuar...")
            return
            
        self.print_header(f"ESTADO DEL HILO: {self.thread_id}")
        
        state = self.make_request("GET", f"threads/{self.thread_id}/state")
        
        if state:
            print("\n--- ESTADO ACTUAL ---")
            print(json.dumps(state, indent=2, ensure_ascii=False))
            
            # Mostrar información relevante
            if "values" in state:
                values = state["values"]
                print("\n--- RESUMEN ---")
                print(f"Título del Proyecto: {values.get('project_title', 'No definido')}")
                print(f"Descripción: {values.get('project_description', 'No definida')}")
                
                if "investment_opportunities" in values:
                    print(f"\nOportunidades de inversión: {len(values['investment_opportunities'])}")
                    
            if "interrupts" in state and state["interrupts"]:
                print("\n⚠️  El hilo está actualmente INTERRUMPIDO")
            else:
                print("\n✅  El hilo NO está interrumpido")
        else:
            print("❌ No se pudo obtener el estado del hilo")
            
        input("\nPresiona Enter para continuar...")

    def run_stateless(self):
        """Ejecuta el agente sin estado."""
        self.print_header("EJECUCIÓN SIN ESTADO")
        
        project_title = input("Título del proyecto: ")
        project_description = input("Descripción del proyecto: ")
        
        payload = {
            "assistant_id": self.assistant_id,
            "input": {
                "project_title": project_title,
                "project_description": project_description
            },
            "on_completion": "delete"
        }
        
        print("\n⏳ Procesando...")
        result = self.make_request("POST", "runs/wait", json=payload)
        
        if result:
            print("\n--- RESULTADO ---")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ No se pudo completar la ejecución sin estado")
            
        input("\nPresiona Enter para continuar...")

    def list_assistants(self):
        """Lista los asistentes disponibles."""
        self.print_header("ASISTENTES DISPONIBLES")
        
        result = self.make_request("POST", "assistants/search", json={})
        
        if result and isinstance(result, list):
            for i, assistant in enumerate(result, 1):
                print(f"\n{i}. ID: {assistant.get('assistant_id')}")
                print(f"   Nombre: {assistant.get('name', 'Sin nombre')}")
                print(f"   Descripción: {assistant.get('description', 'Sin descripción')}")
        else:
            print("❌ No se encontraron asistentes o hubo un error")
            
        input("\nPresiona Enter para continuar...")

    def delete_thread(self):
        """Elimina el hilo actual."""
        if not self.thread_id:
            print("❌ No hay un hilo activo para eliminar")
            input("\nPresiona Enter para continuar...")
            return
            
        confirm = input(f"¿Estás seguro de que deseas eliminar el hilo {self.thread_id}? (s/n): ")
        if confirm.lower() != 's':
            return
            
        result = self.make_request("DELETE", f"threads/{self.thread_id}")
        
        if result and result.get("deleted"):
            print(f"✅ Hilo {self.thread_id} eliminado con éxito")
            self.thread_id = None
        else:
            print(f"❌ No se pudo eliminar el hilo {self.thread_id}")
            
        input("\nPresiona Enter para continuar...")

    def show_menu(self):
        """Muestra el menú principal."""
        while True:
            self.print_header("MENÚ PRINCIPAL - AGENTE LANGGRAPH")
            
            if self.thread_id:
                print(f"Hilo activo: {self.thread_id}")
            else:
                print("No hay hilo activo")
                
            print("\nOpciones:")
            print("1. Crear nuevo hilo")
            print("2. Ejecutar agente")
            print("3. Ver estado del hilo")
            print("4. Ejecutar sin estado")
            print("5. Listar asistentes")
            print("6. Eliminar hilo actual")
            print("0. Salir")
            
            choice = input("\nSelecciona una opción: ")
            
            if choice == "1":
                self.create_thread()
            elif choice == "2":
                self.run_agent()
            elif choice == "3":
                self.view_thread_state()
            elif choice == "4":
                self.run_stateless()
            elif choice == "5":
                self.list_assistants()
            elif choice == "6":
                self.delete_thread()
            elif choice == "0":
                print("\n¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
                input("\nPresiona Enter para continuar...")


def main():
    """Función principal."""
    tester = AgentTester()
    try:
        tester.show_menu()
    except KeyboardInterrupt:
        print("\n\n¡Operación cancelada por el usuario!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        input("Presiona Enter para salir...")
    finally:
        print("\n¡Gracias por usar el probador de agentes!")


if __name__ == "__main__":
    main()
