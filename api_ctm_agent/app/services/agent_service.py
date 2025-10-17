"""Servicio para integrar el agente CTM"""

from typing import Any, Dict, Optional
import sys
import os
import httpx
import asyncio

# Configuración del servidor LangGraph
LANGGRAPH_API_URL = os.getenv("LANGGRAPH_API_URL", "http://127.0.0.1:2024")
USE_LANGGRAPH_SERVER = os.getenv("USE_LANGGRAPH_SERVER", "true").lower() == "true"

# Agregar el path del agente al PYTHONPATH (solo si no usamos el servidor)
agent_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ctm-investment-agent", "src")
if agent_path not in sys.path:
    sys.path.insert(0, agent_path)


class AgentService:
    """Servicio para manejar el agente de inversiones CTM"""
    
    def __init__(self):
        self.agent = None
        self.use_server = USE_LANGGRAPH_SERVER
        self.api_url = LANGGRAPH_API_URL
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Inicializa el agente de inversiones"""
        if self.use_server:
            print(f"🔗 Configurado para usar LangGraph Server en: {self.api_url}")
            self.agent_type = "langgraph_server"
            # Verificar conexión
            try:
                import requests
                response = requests.get(f"{self.api_url}/ok", timeout=2)
                if response.status_code == 200:
                    print("✅ Conexión con LangGraph Server exitosa")
                else:
                    print(f"⚠️ LangGraph Server respondió con status {response.status_code}")
            except Exception as e:
                print(f"⚠️ No se pudo conectar al LangGraph Server: {e}")
                print("   Los requests fallarán hasta que el servidor esté disponible")
        else:
            print("🔧 Modo local: ejecutando agente directamente en la API")
            try:
                # Intentar cargar el grafo de LangGraph
                from agent.graph import graph
                self.agent = graph
                self.agent_type = "langgraph_local"
                print("✅ Agente CTM (LangGraph Local) inicializado correctamente")
            except Exception as e:
                print(f"⚠️ No se pudo inicializar el agente LangGraph: {e}")
                try:
                    # Intentar cargar el pipeline alternativo
                    from agent.flows.pipelines.full_agent import create_full_agent_pipeline
                    self.agent = create_full_agent_pipeline()
                    self.agent_type = "pipeline"
                    print("✅ Agente CTM (Pipeline) inicializado correctamente")
                except Exception as e2:
                    print(f"⚠️ No se pudo inicializar el agente Pipeline: {e2}")
                    print("   Usando modo simulado")
                    self.agent = None
                    self.agent_type = "simulated"
    
    async def process_input(
        self, 
        user_input: Any, 
        thread_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa el input del usuario con el agente
        
        Args:
            user_input: Input del usuario
            thread_id: ID del thread
            config: Configuración adicional
            
        Returns:
            Respuesta del agente
        """
        # Si usamos el servidor de LangGraph
        if self.agent_type == "langgraph_server":
            return await self._call_langgraph_server(user_input, thread_id, config)
        
        # Si no hay agente local, simular
        if self.agent is None:
            return self._simulate_agent_response(user_input)
        
        # Ejecutar agente local
        try:
            # Preparar input para el agente
            agent_input = self._prepare_agent_input(user_input)
            
            # Configuración del agente
            run_config = config or {}
            run_config["configurable"] = run_config.get("configurable", {})
            run_config["configurable"]["thread_id"] = thread_id
            
            # Ejecutar el agente
            result = await self._run_agent(agent_input, run_config)
            
            return result
            
        except Exception as e:
            print(f"❌ Error ejecutando agente: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def _call_langgraph_server(
        self,
        user_input: Any,
        thread_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Llama al servidor de LangGraph via HTTP"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Preparar el payload
                agent_input = self._prepare_agent_input(user_input)
                
                # Buscar o crear assistant
                assistant_id = await self._get_or_create_assistant(client)
                
                # Crear el run
                payload = {
                    "assistant_id": assistant_id,
                    "input": agent_input,
                    "metadata": {},
                    "stream_mode": ["values"]
                }
                
                print(f"📡 Llamando a LangGraph Server: {self.api_url}")
                print(f"   Thread ID: {thread_id}")
                print(f"   Assistant ID: {assistant_id}")
                
                # Hacer el request al servidor
                response = await client.post(
                    f"{self.api_url}/threads/{thread_id}/runs/wait",
                    json=payload,
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Respuesta recibida del LangGraph Server")
                    return {
                        "status": "success",
                        "output": result.get("output", result)
                    }
                else:
                    error_msg = f"LangGraph Server error: {response.status_code}"
                    print(f"❌ {error_msg}")
                    return {
                        "status": "error",
                        "error": error_msg,
                        "details": response.text
                    }
                    
        except httpx.TimeoutException:
            return {
                "status": "error",
                "error": "Timeout al conectar con LangGraph Server"
            }
        except Exception as e:
            print(f"❌ Error llamando a LangGraph Server: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _get_or_create_assistant(self, client: httpx.AsyncClient) -> str:
        """Obtiene o crea un assistant en el servidor de LangGraph"""
        try:
            # Buscar assistants existentes
            response = await client.post(
                f"{self.api_url}/assistants/search",
                json={"graph_id": "agent", "limit": 1}
            )
            
            if response.status_code == 200:
                assistants = response.json()
                if assistants and len(assistants) > 0:
                    return assistants[0]["assistant_id"]
            
            # Si no existe, crear uno nuevo
            response = await client.post(
                f"{self.api_url}/assistants",
                json={
                    "graph_id": "agent",
                    "name": "CTM Investment Agent"
                }
            )
            
            if response.status_code == 200:
                assistant = response.json()
                return assistant["assistant_id"]
            else:
                raise Exception(f"No se pudo crear assistant: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Error obteniendo/creando assistant: {e}")
            # Usar un ID por defecto
            return "agent"
    
    def _prepare_agent_input(self, user_input: Any) -> Dict[str, Any]:
        """Prepara el input para el agente según su tipo"""
        if isinstance(user_input, dict):
            # Si ya es un dict, asegurarse de que tenga la estructura correcta
            if self.agent_type == "langgraph":
                # Para LangGraph, necesitamos la estructura de ProjectState
                return {
                    "project_title": user_input.get("project_title", "Proyecto sin título"),
                    "project_description": user_input.get("project_description", ""),
                    "messages": user_input.get("messages", []),
                    "opportunities": user_input.get("opportunities", []),
                    "selected_opportunities": user_input.get("selected_opportunities", []),
                    "enriched_opportunities": user_input.get("enriched_opportunities", []),
                    "final_report": user_input.get("final_report", "")
                }
            return user_input
        elif isinstance(user_input, str):
            return {
                "project_title": "Proyecto de análisis",
                "project_description": user_input,
                "messages": []
            }
        else:
            return {"input": user_input}
    
    async def _run_agent(self, agent_input: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el agente de forma asíncrona"""
        try:
            import asyncio
            
            print(f"🔄 Ejecutando agente tipo: {self.agent_type}")
            print(f"📥 Input: {agent_input.get('project_title', 'N/A')[:50]}...")
            
            # El agente de LangGraph puede ser síncrono o asíncrono
            if hasattr(self.agent, 'ainvoke'):
                print("   Usando ainvoke (async)")
                result = await self.agent.ainvoke(agent_input, config)
            elif hasattr(self.agent, 'invoke'):
                print("   Usando invoke (sync) con asyncio.to_thread")
                result = await asyncio.to_thread(self.agent.invoke, agent_input, config)
            else:
                raise Exception("El agente no tiene método invoke o ainvoke")
            
            print(f"✅ Agente ejecutado exitosamente")
            print(f"📤 Output keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
            
            return {
                "status": "success",
                "output": result
            }
        except Exception as e:
            print(f"❌ Error en _run_agent: {e}")
            import traceback
            traceback.print_exc()
            raise e
    
    def _simulate_agent_response(self, user_input: Any) -> Dict[str, Any]:
        """Simula una respuesta del agente cuando no está disponible"""
        if isinstance(user_input, dict):
            content = user_input.get("project_description", str(user_input))
        else:
            content = str(user_input)
        
        return {
            "status": "success",
            "output": {
                "messages": [
                    {
                        "role": "assistant",
                        "content": f"[MODO SIMULADO] He analizado tu proyecto: '{content[:100]}...'. "
                                   f"En producción, aquí se ejecutaría el agente completo de análisis de inversiones CTM."
                    }
                ],
                "opportunities": [
                    {
                        "title": "Oportunidad de ejemplo 1",
                        "description": "Esta es una oportunidad simulada",
                        "relevance_score": 0.85
                    }
                ]
            }
        }


# Instancia global del servicio
agent_service = AgentService()
