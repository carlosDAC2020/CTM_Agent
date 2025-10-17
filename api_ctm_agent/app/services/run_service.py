"""Servicio para manejar Runs"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException

from app.models import Run, RunCreate, RunStatus, RunOutput, Message
from .database import db
from .thread_service import ThreadService
from .agent_service import agent_service


class RunService:
    """Servicio para operaciones de Runs"""
    
    @staticmethod
    async def create_run(thread_id: str, data: RunCreate) -> Run:
        """Crea un nuevo run"""
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        run_id = str(uuid4())
        now = datetime.now()
        
        run = Run(
            run_id=run_id,
            thread_id=thread_id,
            assistant_id=data.assistant_id,
            status=RunStatus.PENDING,
            created_at=now,
            updated_at=now,
            metadata=data.metadata,
            multitask_strategy=data.multitask_strategy
        )
        
        db.runs[run_id] = run.model_dump()
        
        # Actualizar estado del thread
        ThreadService.update_thread_state(thread_id, status="busy")
        
        return run
    
    @staticmethod
    async def execute_run(thread_id: str, run_id: str, data: RunCreate) -> RunOutput:
        """Ejecuta un run y espera el resultado"""
        try:
            # Actualizar estado a running
            db.runs[run_id]["status"] = RunStatus.RUNNING.value
            db.runs[run_id]["updated_at"] = datetime.now()
            
            # Guardar mensaje del usuario si existe
            if data.input:
                user_message = RunService._extract_user_message(data.input)
                if user_message:
                    msg = Message(role="user", content=user_message)
                    ThreadService.add_message(thread_id, msg)
            
            # Ejecutar el agente
            result = await agent_service.process_input(
                user_input=data.input,
                thread_id=thread_id,
                config=data.config
            )
            
            # Guardar respuesta del agente
            if result.get("status") == "success":
                assistant_message = RunService._extract_assistant_message(result.get("output"))
                if assistant_message:
                    msg = Message(role="assistant", content=assistant_message)
                    ThreadService.add_message(thread_id, msg)
                
                # Actualizar estado a success
                db.runs[run_id]["status"] = RunStatus.SUCCESS.value
                ThreadService.update_thread_state(thread_id, status="idle")
                
                return RunOutput(
                    run_id=run_id,
                    thread_id=thread_id,
                    status=RunStatus.SUCCESS,
                    output=result.get("output"),
                    metadata=data.metadata
                )
            else:
                # Error en el agente
                db.runs[run_id]["status"] = RunStatus.ERROR.value
                ThreadService.update_thread_state(thread_id, status="error")
                
                return RunOutput(
                    run_id=run_id,
                    thread_id=thread_id,
                    status=RunStatus.ERROR,
                    error=result.get("error", "Error desconocido"),
                    metadata=data.metadata
                )
                
        except Exception as e:
            db.runs[run_id]["status"] = RunStatus.ERROR.value
            ThreadService.update_thread_state(thread_id, status="error")
            
            return RunOutput(
                run_id=run_id,
                thread_id=thread_id,
                status=RunStatus.ERROR,
                error=str(e),
                metadata=data.metadata
            )
    
    @staticmethod
    def _extract_user_message(user_input: Any) -> Optional[str]:
        """Extrae el mensaje del usuario del input"""
        if isinstance(user_input, str):
            return user_input
        elif isinstance(user_input, dict):
            if "messages" in user_input and user_input["messages"]:
                last_msg = user_input["messages"][-1]
                return last_msg.get("content", "")
            elif "project_description" in user_input:
                return user_input["project_description"]
            elif "content" in user_input:
                return user_input["content"]
        return None
    
    @staticmethod
    def _extract_assistant_message(output: Any) -> Optional[str]:
        """Extrae el mensaje del asistente del output"""
        if isinstance(output, str):
            return output
        elif isinstance(output, dict):
            if "messages" in output and output["messages"]:
                last_msg = output["messages"][-1]
                if isinstance(last_msg, dict):
                    return last_msg.get("content", "")
                return str(last_msg)
            elif "content" in output:
                return output["content"]
            else:
                # Convertir todo el output a string
                return str(output)
        return None
    
    @staticmethod
    def get_run(thread_id: str, run_id: str) -> Run:
        """Obtiene un run por ID"""
        if run_id not in db.runs:
            raise HTTPException(status_code=404, detail="Run no encontrado")
        
        run_data = db.runs[run_id]
        if run_data["thread_id"] != thread_id:
            raise HTTPException(status_code=404, detail="Run no pertenece a este thread")
        
        return Run(**run_data)
    
    @staticmethod
    def list_runs(thread_id: str, limit: int = 10, offset: int = 0) -> List[Run]:
        """Lista todos los runs de un thread"""
        if thread_id not in db.threads:
            raise HTTPException(status_code=404, detail="Thread no encontrado")
        
        thread_runs = [
            Run(**data) for data in db.runs.values()
            if data["thread_id"] == thread_id
        ]
        thread_runs.sort(key=lambda x: x.created_at, reverse=True)
        return thread_runs[offset:offset + limit]
    
    @staticmethod
    def cancel_run(thread_id: str, run_id: str) -> Run:
        """Cancela un run en ejecución"""
        if run_id not in db.runs:
            raise HTTPException(status_code=404, detail="Run no encontrado")
        
        run_data = db.runs[run_id]
        if run_data["thread_id"] != thread_id:
            raise HTTPException(status_code=404, detail="Run no pertenece a este thread")
        
        if run_data["status"] in [RunStatus.SUCCESS.value, RunStatus.ERROR.value, RunStatus.CANCELLED.value]:
            raise HTTPException(status_code=400, detail="Run ya ha finalizado")
        
        run_data["status"] = RunStatus.CANCELLED.value
        run_data["updated_at"] = datetime.now()
        
        ThreadService.update_thread_state(thread_id, status="idle")
        
        return Run(**run_data)
