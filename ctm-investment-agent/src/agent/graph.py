# src/agent/graph.py

from langgraph.graph import StateGraph
from agent.state import ProjectState   
from agent.nodes.ingestion import ingest_project_info
# ¡Importamos los nuevos nodos!
from agent.nodes.research import (
    generate_queries_node, 
    search_web_node, 
    scrutinize_results_node, 
    extract_opportunities_node
)
from agent.nodes.analysis import academic_research, generate_report
from agent.nodes.chat import chat_responder, select_opportunities, route_chat, process_selection

builder = StateGraph(ProjectState)

# Añadimos los nodos nuevos y eliminamos el antiguo
builder.add_node("ingest_info", ingest_project_info)
builder.add_node("generate_queries", generate_queries_node)
builder.add_node("search_web", search_web_node)
builder.add_node("scrutinize_results", scrutinize_results_node)
builder.add_node("extract_opportunities", extract_opportunities_node)
builder.add_node("select_opportunities", select_opportunities)
builder.add_node("process_selection", process_selection) 
builder.add_node("academic_research", academic_research)
builder.add_node("generate_report", generate_report)
builder.add_node("chat_responder", chat_responder)

# --- Flujo de la conversación ---
builder.set_entry_point("ingest_info")
builder.add_edge("ingest_info", "generate_queries")
builder.add_edge("generate_queries", "search_web")
builder.add_edge("search_web", "scrutinize_results")
builder.add_edge("scrutinize_results", "extract_opportunities")
builder.add_edge("extract_opportunities", "select_opportunities")
# El resto del flujo permanece igual
builder.add_edge("select_opportunities", "process_selection") 
builder.add_edge("process_selection", "academic_research") 
builder.add_edge("academic_research", "generate_report")
builder.add_edge("generate_report", "chat_responder")

# --- Lógica Condicional (sin cambios) ---
builder.add_conditional_edges(
    "chat_responder",
    route_chat,
    { "continue": "chat_responder", "end": "__end__" }
)

graph = builder.compile()