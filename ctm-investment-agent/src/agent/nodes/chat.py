# src/agent/nodes/chat.py

from typing import Dict, Any
from langgraph.types import interrupt
from ..state import ProjectState
from langchain_core.messages import HumanMessage

def select_opportunities(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo que presenta las oportunidades encontradas y PAUSA la ejecución.
    La lógica de PROCESAMIENTO de la selección se mueve al siguiente nodo en el grafo.
    """
    print("\n" + "="*80)
    print("NODO: PRESENTAR Y PAUSAR PARA SELECCIÓN DE OPORTUNIDADES")
    print("="*80)
    
    opportunities = state.get("investment_opportunities", [])

    print(state)
    
    if not opportunities:
        print("   -> No hay oportunidades para seleccionar. Saltando este paso.")
        # Devolvemos un valor especial para que el siguiente nodo sepa que no hay nada que procesar
        return {"user_selection": "none"}
    
    print(f"\n   Se encontraron {len(opportunities)} oportunidades.")
    print("   Pausando ejecución para esperar selección del usuario...\n")
    
    # Preparamos la información que se enviará al cliente
    opportunities_info = {
        "total_opportunities": len(opportunities),
        "opportunities": [
            {
                "index": idx,
                "origin": opp.get("origin", "N/A"),
                "description": opp.get("description", "N/A"),
                "financing_type": opp.get("financing_type", "N/A"),
                "application_deadline": opp.get("application_deadline", "N/A"),
                "opportunity_url": opp.get("opportunity_url", "N/A")
            }
            for idx, opp in enumerate(opportunities)
        ],
        "instruction": "Por favor, selecciona las oportunidades que deseas analizar. "
                      "Envía una lista de índices (ej: [0, 1, 2]) o 'all' para seleccionar todas."
    }
    
    # Pausamos la ejecución. El valor que el usuario envíe se almacenará en el estado.
    # Cuando se reanude, el valor de 'interrupt()' será la selección del usuario.
    # Lo guardamos en una nueva clave del estado, por ejemplo 'user_selection'.
    return {"user_selection": interrupt(opportunities_info)}


def process_selection(state: ProjectState) -> Dict[str, Any]:
    """
    Este nuevo nodo se ejecuta DESPUÉS de que el usuario haya hecho su selección.
    Su única responsabilidad es procesar esa selección y actualizar el estado final.
    """
    print("\n" + "="*80)
    print("NODO: PROCESANDO SELECCIÓN DEL USUARIO")
    print("="*80)

    user_selection = state.get("user_selection")
    opportunities = state.get("investment_opportunities", [])
    selected_opportunities = []

    if user_selection == "none":
        print("   -> No se encontraron oportunidades, el análisis será omitido.")

    elif isinstance(user_selection, str) and user_selection.lower() == "all":
        selected_opportunities = opportunities
        print(f"   ✅ Usuario seleccionó TODAS las oportunidades ({len(opportunities)})")

    elif isinstance(user_selection, list):
        valid_indices = [idx for idx in user_selection if isinstance(idx, int) and 0 <= idx < len(opportunities)]
        selected_opportunities = [opportunities[idx] for idx in valid_indices]
        print(f"   ✅ Usuario seleccionó {len(selected_opportunities)} oportunidades: {valid_indices}")
        
    else:
        print(f"   ⚠️ Selección inválida recibida: {user_selection}. No se seleccionó ninguna oportunidad.")

    message_content = f"Has seleccionado {len(selected_opportunities)} oportunidades para análisis académico."
    if not selected_opportunities:
        message_content = "No se seleccionó ninguna oportunidad válida. El análisis académico será omitido."

    print(f"\n{message_content}\n")

    # Actualizamos el estado con las oportunidades seleccionadas y borramos la selección temporal
    return {
        "selected_opportunities": selected_opportunities,
        "user_selection": None, # Limpiamos la clave temporal
        "messages": [{"role": "assistant", "content": message_content}]
    }


def chat_responder(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo interactivo que responde preguntas sobre el proyecto, oportunidades y reporte.
    Lee el último mensaje del usuario desde el estado.
    """
    from ..config import get_llm
    from langchain_core.prompts import ChatPromptTemplate
    
    print("\n" + "="*80)
    print("NODO: CHAT INTERACTIVO")
    print("="*80)
    
    # Verificar si hay un reporte generado
    improvement_report = state.get("improvement_report", "")
    
    if not improvement_report or improvement_report == "No se pudo generar el reporte ya que no se encontró investigación académica.":
        print("   -> No hay reporte disponible. Finalizando.")
        return {}
    
    print("\n   ✅ Reporte completo disponible (con propuesta conceptual)")
    print("   ✅ Sistema de preguntas y respuestas activado")
    
    # Preparar información para el usuario
    chat_info = {
        "status": "ready",
        "message": "El reporte de mejoras y la propuesta conceptual están listos. Puedes hacer preguntas sobre:",
        "topics": [
            "El proyecto y sus componentes",
            "Las oportunidades de financiación identificadas",
            "Las recomendaciones del reporte",
            "La propuesta conceptual",
            "Cómo implementar las mejoras sugeridas",
            "Alineación con oportunidades de financiación"
        ],
        "instruction": "Envía tu pregunta como texto. Envía 'end' para finalizar."
    }
    
    print("\n   Puedes hacer preguntas sobre:")
    for topic in chat_info["topics"]:
        print(f"      • {topic}")
    
    print("\n   Esperando pregunta del usuario...")
    
    # Pausar y esperar pregunta del usuario
    user_input = interrupt(chat_info)
    
    # Convertir input a string
    if isinstance(user_input, dict):
        question = user_input.get("question", user_input.get("text", str(user_input)))
    else:
        question = str(user_input)
    
    print(f"\n   ➡️ Procesando pregunta: {question[:60]}...")
    
    # Verificar si el usuario quiere finalizar
    if question.lower().strip() in ["end", "fin", "finalizar", "salir", "exit"]:
        print("   ✅ Finalizando sesión interactiva")
        return {
            "messages": [{
                "role": "assistant",
                "content": "Sesión finalizada. Gracias por usar el agente CTM."
            }]
        }
    
    # Responder la pregunta
    llm = get_llm()
    
    project_title = state.get("project_title", "Proyecto")
    project_description = state.get("project_description", "")
    investment_opportunities = state.get("investment_opportunities", [])
    academic_papers = state.get("academic_papers", [])
    
    # Preparar contexto de oportunidades
    opportunities_context = "\n".join([
        f"- {opp.get('origin', 'N/A')}: {opp.get('description', 'N/A')} (Tipo: {opp.get('financing_type', 'N/A')}, Deadline: {opp.get('application_deadline', 'N/A')})"
        for opp in investment_opportunities[:10]
    ]) if investment_opportunities else "No se encontraron oportunidades."
    
    # Preparar contexto de papers
    papers_context = "\n".join([
        f"- [{paper.get('source', 'N/A')}] {paper.get('title', 'N/A')}"
        for paper in academic_papers[:5]
    ]) if academic_papers else "No hay papers disponibles."
    
    prompt = ChatPromptTemplate.from_template(
        """Eres un asistente experto en innovación y financiación de proyectos tecnológicos.
        Ayudas a entender el proyecto, las oportunidades de financiación y las recomendaciones de mejora.
        
        PROYECTO:
        Título: {project_title}
        Descripción: {project_description}
        
        OPORTUNIDADES DE FINANCIACIÓN ENCONTRADAS:
        {opportunities_context}
        
        REPORTE COMPLETO (Recomendaciones + Propuesta Conceptual):
        {improvement_report}
        
        PAPERS ACADÉMICOS CONSULTADOS:
        {papers_context}
        
        PREGUNTA DEL USUARIO:
        {question}
        
        INSTRUCCIONES:
        - Proporciona una respuesta clara, concisa y accionable
        - Usa el contexto disponible para fundamentar tu respuesta
        - Si la pregunta es sobre oportunidades, menciona las más relevantes
        - Si es sobre implementación, refiérenciate en las recomendaciones del reporte
        - Si la información no está disponible, indícalo claramente
        
        RESPUESTA:
        """
    )
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "project_title": project_title,
            "project_description": project_description,
            "opportunities_context": opportunities_context,
            "improvement_report": improvement_report,
            "papers_context": papers_context,
            "question": question
        })
        
        answer = response.content
        print("   ✅ Respuesta generada\n")
        
        return {
            "messages": [
                # ¡Añadimos el mensaje del usuario al estado!
                HumanMessage(content=question),
                # Y luego añadimos la respuesta del asistente
                {"role": "assistant", "content": answer}
            ]
        }
        
    except Exception as e:
        print(f"   ⚠️ Error respondiendo pregunta: {e}")
        return {
            "messages": [{
                "role": "assistant",
                "content": f"Error al responder la pregunta: {str(e)}"
            }]
        }


def route_chat(state: ProjectState) -> str:
    """
    Decide si continuar en el bucle de chat o finalizar la conversación.
    Solo procesa mensajes del usuario, no del asistente.
    """
    messages = state.get("messages", [])
    
    if not messages:
        print("--- ROUTER: No hay mensajes, finalizando ---")
        return "end"
    
    # Buscar el último mensaje del USUARIO (no del asistente)
    last_user_message = None
    for msg in reversed(messages):
        # Verificar si es un mensaje del usuario
        is_user = False
        if isinstance(msg, dict):
            is_user = msg.get("role") == "user" or msg.get("type") == "human"
        elif hasattr(msg, "type"):
            is_user = msg.type == "human"
        
        if is_user:
            last_user_message = msg
            break
    
    if not last_user_message:
        print("--- ROUTER: No hay mensajes del usuario, finalizando ---")
        return "end"
    
    # Extraer el contenido del mensaje del usuario
    content = ""
    if isinstance(last_user_message, dict):
        content = last_user_message.get("content", "")
    elif hasattr(last_user_message, "content"):
        content = last_user_message.content
    
    # Extraer el texto
    question = ""
    if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
        question = content[0].get("text", "")
    elif isinstance(content, str):
        question = content
    else:
        question = str(content)
        
    print(f"--- ROUTER: Verificando entrada del usuario '{question[:100]}' ---")
    
    if question.lower().strip() in ["end", "fin", "finalizar", "salir", "exit"]:
        print("   -> Decisión: Finalizar")
        return "end"
    else:
        print("   -> Decisión: Continuar chat")
        return "continue"