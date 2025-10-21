
from typing import Dict, Any, List
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate 

from ..state import ProjectState
from ..config import get_llm


# --- MODELO DE DATOS PARA LA DECISIÓN DEL CHAT ---
class ChatDecision(BaseModel):
    """
    Clasifica la intención del usuario y extrae la información necesaria.
    """
    response: str = Field(description="La respuesta conversacional directa a la pregunta del usuario.")
    action: str = Field(
        description="La acción a seguir. Debe ser una de: 'continue' (para seguir chateando), 'rerun_research' (para investigar de nuevo), 'specific_report' (para generar un reporte de una oportunidad), o 'end' (para finalizar)."
    )
    target_index: int = Field(
        default=None, 
        description="Si la acción es 'specific_report', este es el índice numérico de la oportunidad mencionada por el usuario."
    )



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
    Nodo interactivo que responde preguntas y determina la siguiente acción del grafo.
    """
    print("\n" + "="*80)
    print("NODO: CHAT INTERACTIVO (Centro de Comando)")
    print("="*80)
    
    # Pausar y esperar pregunta del usuario
    user_input = interrupt({ "status": "ready", "instruction": "Envía tu pregunta o comando." })
    
    # Asumimos que la entrada es un string simple
    question = str(user_input)
    print(f"\n   ➡️ Procesando entrada: {question[:80]}...")
    
    # --- LÓGICA DE CLASIFICACIÓN DE INTENCIÓN ---
    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=ChatDecision)

    # Formatear la lista de oportunidades para el prompt
    opportunities_summary = "\n".join([
        f"Índice {idx}: {opp.get('origin', 'N/A')} - {opp.get('description', 'N/A')[:100]}..."
        for idx, opp in enumerate(state.get("investment_opportunities", []))
    ])

    system_prompt = f"""
    Eres un asistente experto que actúa como un centro de comando. Tu tarea es doble:
    1. Responder a la pregunta del usuario de forma conversacional.
    2. Clasificar la intención del usuario en una de las siguientes acciones:
       - 'continue': Si es una pregunta general o una conversación normal.
       - 'rerun_research': Si el usuario pide explícitamente "investiga de nuevo", "busca más oportunidades", "encuentra otras opciones", etc.
       - 'specific_report': Si el usuario pide generar un reporte detallado, analizar o profundizar en UNA oportunidad específica. Debes identificar el ÍNDICE de esa oportunidad.
       - 'end': Si el usuario quiere terminar la conversación ("adiós", "fin", "terminar").

    Aquí están las oportunidades disponibles con sus índices:
    {opportunities_summary}

    Analiza la pregunta del usuario y devuelve SIEMPRE un objeto JSON con el formato especificado.
    
     Ejemplo 1:
    Usuario: "Explícame la recomendación 2."
    Tu salida JSON: {{{{ "response": "Claro, la recomendación 2 se enfoca en...", "action": "continue", "target_index": null }}}}

    Ejemplo 2:
    Usuario: "Busca otras alternativas, por favor."
    Tu salida JSON: {{{{ "response": "Entendido, iniciando una nueva búsqueda para encontrar alternativas.", "action": "rerun_research", "target_index": null }}}}
    
    Ejemplo 3:
    Usuario: "Haz un reporte detallado de la oportunidad con índice 1."
    Tu salida JSON: {{{{ "response": "Perfecto, comenzaré a generar el reporte para la oportunidad 1.", "action": "specific_report", "target_index": 1 }}}}

    {{format_instructions}}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | parser

    try:
        decision = chain.invoke({
            "question": question,
            "format_instructions": parser.get_format_instructions()
        })
        
        print(f"   ✅ Decisión del LLM: Acción='{decision.get('action')}', Índice='{decision.get('target_index')}'")
        
        return {
            "messages": [
                HumanMessage(content=question),
                {"role": "assistant", "content": decision.get("response")}
            ],
            "next_action": decision.get("action"),
            "action_input": decision.get("target_index")
        }

    except Exception as e:
        print(f"   ⚠️ Error en la decisión del chat: {e}")
        return {
            "messages": [
                HumanMessage(content=question),
                {"role": "assistant", "content": f"Hubo un error al procesar tu solicitud: {e}"}
            ],
            "next_action": "continue" # Por seguridad, volvemos a chatear
        }

# --- NUEVO ROUTER INTELIGENTE ---
def route_chat(state: ProjectState) -> str:
    """
    Lee el campo 'next_action' del estado para decidir a dónde ir.
    """
    action = state.get("next_action")
    print(f"\n--- ROUTER: Decidiendo la ruta basada en la acción '{action}' ---")
    
    if action == "rerun_research":
        return "rerun_research"
    elif action == "specific_report":
        return "specific_report"
    elif action == "end":
        return "end"
    else: # Por defecto o si es 'continue'
        return "continue"