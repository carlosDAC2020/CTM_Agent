# src/agent/graph.py

from langgraph.graph import StateGraph

# --- Importa la nueva función ROUTER ---
from agent.state import ProjectState   
from agent.nodes.ingestion import ingest_project_info
from agent.nodes.research import research_opportunities
from agent.nodes.analysis import academic_research, generate_report
from agent.nodes.chat import chat_responder, select_opportunities, route_chat, process_selection

builder = StateGraph(ProjectState)

# (Los nodos se añaden 
builder.add_node("ingest_info", ingest_project_info)
builder.add_node("research_opportunities", research_opportunities)
builder.add_node("select_opportunities", select_opportunities)
builder.add_node("process_selection", process_selection) 
builder.add_node("academic_research", academic_research)
builder.add_node("generate_report", generate_report)
builder.add_node("chat_responder", chat_responder)

# --- Flujo de la conversación ---
builder.set_entry_point("ingest_info")
builder.add_edge("ingest_info", "research_opportunities")
builder.add_edge("research_opportunities", "select_opportunities")
# Ahora, después de la interrupción, procesamos la selección
builder.add_edge("select_opportunities", "process_selection") 
# Y después de procesar, continuamos con la investigación académica
builder.add_edge("process_selection", "academic_research") 
builder.add_edge("academic_research", "generate_report")
builder.add_edge("generate_report", "chat_responder")

# ---  LÓGICA DE BUCLE CONDICIONAL ---
# Después de que 'chat_responder' se ejecute, llamamos a 'route_chat' para decidir qué hacer.
builder.add_conditional_edges(
    "chat_responder",
    route_chat,
    {
        "continue": "chat_responder", # Si la función devuelve "continue", vuelve a ejecutar el chat.
        "end": "__end__"             # Si la función devuelve "end", termina el grafo.
    }
)

# (Ya no necesitamos la línea 'builder.add_edge("chat_responder", "__end__")')

# Compilamos el grafo como antes, pero sin el checkpointer manual.
# LangGraph Studio maneja la persistencia y la interrupción se define en los nodos.
graph = builder.compile()