# src/agent/graph.py

from langgraph.graph import StateGraph
from agent.state import ProjectState   
from agent.nodes.ingestion import ingest_project_info

# Importamos los nodos de búsqueda de financiación
from agent.nodes.research import (
    generate_funding_queries_node, 
    search_web_node, 
    scrutinize_results_node, 
    extract_opportunities_node
)
# Importamos los nodos de análisis y reporte
from agent.nodes.analysis import (
    generate_academic_queries_node, # ¡Nuevo!
    academic_research, 
    generate_state_of_the_art_report, # ¡Renombrado!
    generate_specific_report
)
# Importamos los nodos de chat
from agent.nodes.chat import (
    chat_responder, 
    select_opportunities, 
    route_chat, 
    process_selection
)
from agent.nodes.storage import save_report_as_pdf

builder = StateGraph(ProjectState)

# --- 1. REGISTRAR TODOS LOS NODOS ---
# Nodos de Ingesta
builder.add_node("ingest_info", ingest_project_info)
# Nodos del Flujo Principal (Estado del Arte)
builder.add_node("generate_academic_queries", generate_academic_queries_node)
builder.add_node("academic_research", academic_research)
builder.add_node("generate_state_of_the_art_report", generate_state_of_the_art_report)
# Nodos del Flujo Secundario (Financiación)
builder.add_node("generate_funding_queries", generate_funding_queries_node)
builder.add_node("search_web", search_web_node)
builder.add_node("scrutinize_results", scrutinize_results_node)
builder.add_node("extract_opportunities", extract_opportunities_node)
builder.add_node("select_opportunities", select_opportunities)
builder.add_node("process_selection", process_selection)
# Nodos de Reportes Específicos y Guardado
builder.add_node("generate_specific_report", generate_specific_report)
builder.add_node("save_report_as_pdf", save_report_as_pdf)
# Nodo Central de Chat
builder.add_node("chat_responder", chat_responder)

# --- 2. CONECTAR EL NUEVO FLUJO PRINCIPAL ---
builder.set_entry_point("ingest_info")
builder.add_edge("ingest_info", "generate_academic_queries")
builder.add_edge("generate_academic_queries", "academic_research")
builder.add_edge("academic_research", "generate_state_of_the_art_report")
builder.add_edge("generate_state_of_the_art_report", "save_report_as_pdf")
builder.add_edge("save_report_as_pdf", "chat_responder")

# --- 3. CONECTAR LOS FLUJOS SECUNDARIOS (QUE SALEN DEL CHAT) ---

# Flujo para generar un reporte específico
builder.add_edge("generate_specific_report", "save_report_as_pdf")

# Flujo completo para buscar financiación
builder.add_edge("generate_funding_queries", "search_web")
builder.add_edge("search_web", "scrutinize_results")
builder.add_edge("scrutinize_results", "extract_opportunities")
builder.add_edge("extract_opportunities", "select_opportunities")
builder.add_edge("select_opportunities", "process_selection") 
builder.add_edge("process_selection", "chat_responder")


# --- 4. DEFINIR LAS RUTAS CONDICIONALES ---
builder.add_conditional_edges(
    "chat_responder",
    route_chat,
    {
        "continue": "chat_responder",
        "find_funding": "generate_funding_queries", 
        "specific_report": "generate_specific_report",
        "end": "__end__"
    }
)

# --- 5. COMPILAR EL GRAFO ---
graph = builder.compile()