# src/agent/graph.py

from langgraph.graph import StateGraph
from agent.state import ProjectState   
from agent.nodes.ingestion import ingest_project_info
from agent.nodes.research import (
    generate_queries_node, 
    search_web_node, 
    scrutinize_results_node, 
    extract_opportunities_node
)
from agent.nodes.analysis import (
    academic_research, 
    generate_report, 
    generate_specific_report
)
from agent.nodes.chat import (
    chat_responder, 
    select_opportunities, 
    route_chat, 
    process_selection
)

from agent.nodes.storage import save_report_as_pdf

# ============================================================================
# CONSTRUCCIÓN DEL GRAFO
# ============================================================================

builder = StateGraph(ProjectState)

# --- 1. AÑADIMOS TODOS LOS NODOS AL GRAFO ---

# Nodos del flujo principal
builder.add_node("ingest_info", ingest_project_info)
builder.add_node("generate_queries", generate_queries_node)
builder.add_node("search_web", search_web_node)
builder.add_node("scrutinize_results", scrutinize_results_node)
builder.add_node("extract_opportunities", extract_opportunities_node)
builder.add_node("select_opportunities", select_opportunities)
builder.add_node("process_selection", process_selection) 
builder.add_node("academic_research", academic_research)

# Nodos de generación y guardado de reportes
builder.add_node("generate_report", generate_report)
builder.add_node("generate_specific_report", generate_specific_report)
builder.add_node("save_report_as_pdf", save_report_as_pdf)

# Nodo central de chat
builder.add_node("chat_responder", chat_responder)


# --- 2. CONECTAMOS LOS NODOS CON ARISTAS (EDGES) ---

builder.set_entry_point("ingest_info")

# Flujo de investigación hasta el reporte general
builder.add_edge("ingest_info", "generate_queries")
builder.add_edge("generate_queries", "search_web")
builder.add_edge("search_web", "scrutinize_results")
builder.add_edge("scrutinize_results", "extract_opportunities")
builder.add_edge("extract_opportunities", "select_opportunities")
builder.add_edge("select_opportunities", "process_selection") 
builder.add_edge("process_selection", "academic_research") 
builder.add_edge("academic_research", "generate_report")

# --- ¡SECUENCIA DE GUARDADO ---
# Después de generar CUALQUIER tipo de reporte, lo guardamos como PDF.
builder.add_edge("generate_report", "save_report_as_pdf")
builder.add_edge("generate_specific_report", "save_report_as_pdf")

# Después de guardar el PDF, volvemos directamente al chat.
builder.add_edge("save_report_as_pdf", "chat_responder")


# --- 3. DEFINIMOS LAS RUTAS CONDICIONALES DESDE EL CHAT ---
builder.add_conditional_edges(
    "chat_responder",
    route_chat,
    {
        "continue": "chat_responder",
        "rerun_research": "generate_queries",
        "specific_report": "generate_specific_report",
        "end": "__end__"
    }
)

# --- 4. COMPILAMOS EL GRAFO ---
graph = builder.compile()