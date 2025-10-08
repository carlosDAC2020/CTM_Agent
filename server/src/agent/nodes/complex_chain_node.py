"""Nodo que ejecuta un flujo complejo de LangChain."""

from typing import Any, Dict
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dataclasses import asdict

from ..state import State, Context
from ..config import get_llm
from ..events import AgentEvent


async def complex_chain(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Nodo que ejecuta un flujo complejo de LangChain.
    
    Este flujo implementa un proceso multi-paso:
    1. Análisis de la consulta
    2. Generación de sub-preguntas
    3. Respuesta a cada sub-pregunta
    4. Síntesis final
    
    Args:
        state: Estado actual del agente
        runtime: Runtime de LangGraph
        
    Returns:
        Diccionario con la respuesta sintetizada
    """
    events = list(state.events)  # Copiar eventos existentes
    
    # Evento de inicio
    events.append(asdict(AgentEvent.node_start("complex_chain", "Iniciando flujo complejo")))
    
    last_message = state.messages[-1]
    user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    llm = get_llm()
    
    # Paso 1: Analizar la consulta
    events.append(asdict(AgentEvent.step("complex_chain", "analysis", "Analizando consulta y descomponiendo en sub-preguntas")))
    
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente que analiza consultas complejas y las descompone en pasos."),
        ("human", "Analiza esta consulta y descomponla en 2-3 sub-preguntas específicas: {query}")
    ])
    analysis_chain = analysis_prompt | llm | StrOutputParser()
    
    events.append(asdict(AgentEvent.tool_call("complex_chain", "llm_analysis", {"query": user_input})))
    sub_questions = await analysis_chain.ainvoke({"query": user_input})
    events.append(asdict(AgentEvent.tool_result("complex_chain", "llm_analysis", sub_questions)))
    
    # Paso 2: Responder cada sub-pregunta
    events.append(asdict(AgentEvent.step("complex_chain", "qa", "Respondiendo sub-preguntas generadas")))
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente experto que responde preguntas de forma concisa y precisa."),
        ("human", "{question}")
    ])
    qa_chain = qa_prompt | llm | StrOutputParser()
    
    events.append(asdict(AgentEvent.tool_call("complex_chain", "llm_qa", {"questions": sub_questions})))
    answers = await qa_chain.ainvoke({"question": sub_questions})
    events.append(asdict(AgentEvent.tool_result("complex_chain", "llm_qa", answers)))
    
    # Paso 3: Síntesis final
    events.append(asdict(AgentEvent.step("complex_chain", "synthesis", "Sintetizando respuesta final")))
    
    synthesis_prompt = ChatPromptTemplate.from_messages([
        ("system", "Sintetiza la siguiente información en una respuesta coherente y completa."),
        ("human", "Pregunta original: {original_query}\n\nAnálisis y respuestas: {answers}\n\nProporciona una respuesta final integrada.")
    ])
    synthesis_chain = synthesis_prompt | llm | StrOutputParser()
    
    events.append(asdict(AgentEvent.tool_call("complex_chain", "llm_synthesis", {
        "original_query": user_input,
        "answers": answers
    })))
    final_response = await synthesis_chain.ainvoke({
        "original_query": user_input,
        "answers": answers
    })
    events.append(asdict(AgentEvent.tool_result("complex_chain", "llm_synthesis", final_response)))
    
    # Evento de finalización
    events.append(asdict(AgentEvent.message("complex_chain", final_response)))
    events.append(asdict(AgentEvent.node_end("complex_chain", "Flujo complejo completado")))
    
    return {
        "messages": [AIMessage(content=final_response)],
        "complex_chain_result": final_response,
        "events": events,
        "next_node": None
    }
