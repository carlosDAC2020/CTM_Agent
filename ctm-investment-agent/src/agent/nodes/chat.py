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
        description="La acción a seguir. Debe ser una de: 'continue' (para seguir chateando), 'find_funding' (para buscar financiación), 'specific_report' (para generar un reporte de una oportunidad), o 'end' (para finalizar)."
    )
    target_index: int = Field(
        default=None, 
        description="Si la acción es 'specific_report', este es el índice numérico de la oportunidad mencionada por el usuario."
    )


def select_opportunities(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo que presenta las oportunidades de la ÚLTIMA búsqueda.
    ✅ Ahora solo muestra las oportunidades nuevas, no todo el historial.
    """
    print("\n" + "="*80)
    print("NODO: PRESENTAR Y PAUSAR PARA SELECCIÓN DE OPORTUNIDADES")
    print("="*80)
    
    # ✅ Obtener SOLO las oportunidades de la última búsqueda
    current_opportunities = state.get("investment_opportunities", [])
    
    if not current_opportunities:
        print("   -> No hay nuevas oportunidades para seleccionar.")
        return {
            "user_selection": "none",
            "investment_opportunities": []
        }
    
    print(f"\n   Se encontraron {len(current_opportunities)} nuevas oportunidades.")
    print("   Pausando ejecución para esperar selección del usuario...\n")
    
    opportunities_info = {
        "total_opportunities": len(current_opportunities),
        "opportunities": [
            {
                "index": idx,
                "origin": opp.get("origin", "N/A"),
                "description": opp.get("description", "N/A"),
                "financing_type": opp.get("financing_type", "N/A"),
                "application_deadline": opp.get("application_deadline", "N/A"),
                "opportunity_url": opp.get("opportunity_url", "N/A")
            }
            for idx, opp in enumerate(current_opportunities)
        ],
        "instruction": "Por favor, selecciona las oportunidades que deseas analizar. "
                      "Envía una lista de índices (ej: [0, 1, 2]) o 'all' para seleccionar todas."
    }
    
    return {
        "user_selection": interrupt(opportunities_info),
        "investment_opportunities": current_opportunities
    }


def process_selection(state: ProjectState) -> Dict[str, Any]:
    """
    Procesa la selección del usuario.
    ✅ Las seleccionadas se AÑADEN a las ya existentes (acumulación).
    """
    print("\n" + "="*80)
    print("NODO: PROCESANDO SELECCIÓN DEL USUARIO")
    print("="*80)

    user_selection = state.get("user_selection")
    # ✅ Oportunidades de la última búsqueda
    current_opportunities = state.get("investment_opportunities", [])
    # ✅ Oportunidades YA seleccionadas previamente
    previously_selected = state.get("selected_opportunities", [])
    
    newly_selected = []

    if user_selection == "none":
        print("   -> No hay oportunidades nuevas.")
        message_content = "No se encontraron nuevas oportunidades en esta búsqueda."

    elif isinstance(user_selection, str) and user_selection.lower() == "all":
        newly_selected = current_opportunities
        print(f"   ✅ Usuario seleccionó TODAS las nuevas oportunidades ({len(newly_selected)})")
        message_content = f"Has seleccionado {len(newly_selected)} nuevas oportunidades para análisis."

    elif isinstance(user_selection, list):
        valid_indices = [
            idx for idx in user_selection 
            if isinstance(idx, int) and 0 <= idx < len(current_opportunities)
        ]
        newly_selected = [current_opportunities[idx] for idx in valid_indices]
        print(f"   ✅ Usuario seleccionó {len(newly_selected)} oportunidades: {valid_indices}")
        message_content = f"Has seleccionado {len(newly_selected)} nuevas oportunidades para análisis."
        
    else:
        print(f"   ⚠️ Selección inválida: {user_selection}")
        message_content = "Selección inválida. No se añadieron oportunidades."

    # ✅ ACUMULAR: Combinar las previamente seleccionadas con las nuevas
    total_selected = previously_selected + newly_selected
    
    print(f"\n   📊 Total acumulado de oportunidades seleccionadas: {len(total_selected)}\n")

    return {
        "selected_opportunities": total_selected,  # ✅ Acumulación
        "user_selection": None,
        "investment_opportunities": [],  # ✅ Limpiar las de la búsqueda actual
        "messages": [{
            "role": "assistant", 
            "content": f"{message_content}\n\nTotal acumulado para análisis: {len(total_selected)} oportunidades."
        }]
    }


def chat_responder(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo interactivo del chat.
    ✅ Ahora reporta correctamente el historial completo.
    """
    print("\n" + "="*80)
    print("NODO: CHAT INTERACTIVO (Centro de Comando)")
    print("="*80)
    
    # ✅ Mostrar información del historial completo
    total_history = len(state.get("all_opportunities_history", []))
    total_selected = len(state.get("selected_opportunities", []))
    
    user_input = interrupt({ 
        "status": "ready", 
        "instruction": "Envía tu pregunta o comando.",
        "current_state": {
            "total_opportunities_found": total_history,  # ✅ Historial completo
            "selected_for_analysis": total_selected,
            "academic_papers": len(state.get("academic_papers", [])),
            "reports_generated": len(state.get("report_paths", []))
        }
    })
    
    question = str(user_input)
    print(f"\n   ➡️ Procesando entrada: {question[:80]}...")
    
    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=ChatDecision)

    # ✅ Formatear el HISTORIAL COMPLETO para el prompt
    all_history = state.get("all_opportunities_history", [])
    opportunities_summary = "\n".join([
        f"Índice {idx}: {opp.get('origin', 'N/A')} - {opp.get('description', 'N/A')[:100]}..."
        for idx, opp in enumerate(all_history)
    ]) if all_history else "No hay oportunidades en el historial aún."

    system_prompt ="""
    **Tu Rol:** Eres un dispatcher de intenciones. Tu única función es analizar el input del usuario y clasificarlo en una acción específica. Eres extremadamente preciso.

    **Acciones Válidas:**
    1.  `find_funding`: Dispara una NUEVA búsqueda de oportunidades de financiación. Se activa con frases como:
        - "Busca financiación para el proyecto"
        - "Encuentra nuevas oportunidades"
        - "Investiga opciones de grants"
        - "Necesito más alternativas de inversión"
    2.  `specific_report`: Dispara la generación de un reporte para UNA oportunidad ya existente en el historial. Se activa con frases que mencionan un índice o un nombre de oportunidad.
        - "Analiza la oportunidad 0"
        - "Dame un reporte sobre la de Minciencias"
        - "Profundiza en la segunda opción"
    3.  `continue`: Para CUALQUIER OTRA PREGUNTA. Si el usuario pide un resumen, pregunta "qué oportunidades hay", o simplemente conversa, la acción es 'continue'.
    4.  `end`: Si el usuario quiere terminar la sesión ("adiós", "fin", "terminar").

    **Contexto (Historial de Oportunidades Encontradas):**
    {opportunities_summary}

    **Tarea:**
    1.  Analiza la pregunta del usuario: `{question}`
    2.  Determina la **acción** correcta según las reglas de arriba.
    3.  Si la acción es `specific_report`, extrae el **índice numérico** correspondiente.
    4.  Genera una **respuesta** conversacional corta que confirme la acción.
    5.  Devuelve un objeto JSON con el formato exacto.

    **Ejemplos de Decisión:**

    - Usuario: "¿Qué oportunidades hemos encontrado hasta ahora?"
      - Acción: `continue` (Es una pregunta, no un comando de acción)
      - JSON: {{{{ "response": "Hasta ahora, hemos encontrado las siguientes oportunidades...", "action": "continue", "target_index": null }}}}

    - Usuario: "investiga nuevas oportunidades de financiamiento"
      - Acción: `find_funding` (Es un comando de acción explícito)
      - JSON: {{{{ "response": "Entendido. Iniciando una nueva búsqueda de oportunidades de financiación.", "action": "find_funding", "target_index": null }}}}

    - Usuario: "Analiza la oportunidad con índice 1, por favor."
      - Acción: `specific_report` (Comando de acción con un objetivo claro)
      - JSON: {{{{ "response": "Claro, generando un análisis detallado para la oportunidad 1.", "action": "specific_report", "target_index": 1 }}}}

    {{format_instructions}}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{{question}}")
    ])
    
    chain = prompt | llm | parser

    try:
        decision = chain.invoke({
            "question": question,
            "opportunities_summary": opportunities_summary,
            "total_history": total_history,
            "total_selected": total_selected,
            "format_instructions": parser.get_format_instructions()
        })
        
        action = decision.get("action", "continue")
        target_index = decision.get("target_index")
        
        print(f"   ✅ Decisión del LLM: Acción='{action}', Índice='{target_index}'")
        
        return {
            "messages": [
                HumanMessage(content=question),
                {"role": "assistant", "content": decision.get("response")}
            ],
            "next_action": action,
            "action_input": target_index,
            "all_opportunities_history": all_history,
            "selected_opportunities": state.get("selected_opportunities", []),
            "academic_papers": state.get("academic_papers", []),
            "report_paths": state.get("report_paths", []),
        }

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {
            "messages": [
                HumanMessage(content=question),
                {"role": "assistant", "content": f"Error: {e}"}
            ],
            "next_action": "continue",
            "all_opportunities_history": all_history,
            "selected_opportunities": state.get("selected_opportunities", []),
        }

        
# --- ROUTER INTELIGENTE ---
def route_chat(state: ProjectState) -> str:
    """
    Lee el campo 'next_action' del estado para decidir a dónde ir.
    """
    action = state.get("next_action", "continue")
    print(f"\n--- ROUTER: Decidiendo la ruta basada en la acción '{action}' ---")
    
    if action == "find_funding": 
        return "find_funding"
    elif action == "specific_report":
        return "specific_report"
    elif action == "end":
        return "end"
    else:  # Por defecto o si es 'continue'
        return "continue"