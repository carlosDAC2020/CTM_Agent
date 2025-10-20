# src/agent/nodes/analysis.py

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# --- ¡NUEVAS IMPORTACIONES PARA HERRAMIENTAS ACADÉMICAS! ---
from langchain_community.retrievers import ArxivRetriever
from langchain_community.utilities.semanticscholar import SemanticScholarAPIWrapper

from ..state import ProjectState
from ..config import get_llm


# Modelo para las queries académicas
class AcademicQueries(BaseModel):
    """Lista de queries de búsqueda académica."""
    queries: List[str] = Field(description="Lista de 3 queries de búsqueda para papers académicos")

# --- NODO 1: INVESTIGACIÓN ACADÉMICA (VERSIÓN CON HERRAMIENTAS ESPECIALIZADAS) ---

def academic_research(state: ProjectState) -> Dict[str, Any]:
    """
    Busca papers académicos relevantes usando Arxiv y Semantic Scholar.
    """
    print("\n" + "="*80)
    print("NODO: INVESTIGACIÓN ACADÉMICA")
    print("="*80)
    
    selected_opportunities = state.get("selected_opportunities")
    if not selected_opportunities:
        print("   -> No hay oportunidades seleccionadas. Saltando este paso.")
        return {"academic_papers": []}
    
    print(f"\n   Analizando {len(selected_opportunities)} oportunidades seleccionadas...")
        
    llm = get_llm()
    
    # --- 1. Inicializar las herramientas especializadas ---
    print("   -> Inicializando herramientas: Arxiv, Semantic Scholar")
    try:
        arxiv_retriever = ArxivRetriever(load_max_docs=2, doc_content_chars_max=1000)
        semantic_scholar = SemanticScholarAPIWrapper(top_k_results=3)
    except Exception as e:
        print(f"   Error inicializando herramientas: {e}")
        return {"academic_papers": []}

    # --- 2. Generar múltiples queries de búsqueda ---
    parser = JsonOutputParser(pydantic_object=AcademicQueries)
    
    system_prompt = """Eres un asistente de investigación académica. 
    Basado en un proyecto y las oportunidades de financiación seleccionadas, 
    genera 3 queries de búsqueda efectivas para encontrar papers relevantes en ArXiv y Semantic Scholar.
    
    Usa términos técnicos y concisos en inglés. Enfócate en los aspectos técnicos y científicos del proyecto.
    
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "PROYECTO: {project_description}\n\nOPORTUNIDADES SELECCIONADAS:\n{opportunity}")
    ])
    
    query_generation_chain = prompt | llm | parser
    opportunities_summary = "\n".join([f"- {opp.get('description', '')}" for opp in selected_opportunities])
    
    print("\n[1/3] Generando queries de búsqueda académica...")
    try:
        response = query_generation_chain.invoke({
            "project_description": state["project_description"],
            "opportunity": opportunities_summary,
            "format_instructions": parser.get_format_instructions()
        })
        search_queries = response.get('queries', [])
        print(f"   Generadas {len(search_queries)} queries")
        for idx, q in enumerate(search_queries, 1):
            print(f"      {idx}. {q}")
    except Exception as e:
        print(f"   Error generando queries académicas: {e}")
        import traceback
        traceback.print_exc()
        return {"academic_papers": []}

    # --- 3. Ejecutar búsquedas en ambas herramientas ---
    print("\n[2/3] Buscando papers académicos...")
    all_papers = []
    
    for idx, query in enumerate(search_queries, 1):
        print(f"\n   Query {idx}/{len(search_queries)}: '{query[:60]}...'")
        
        # Búsqueda en Arxiv
        try:
            print("      → Buscando en Arxiv...")
            arxiv_docs = arxiv_retriever.invoke(query)
            print(f"        Arxiv: {len(arxiv_docs)} documentos")
            for doc in arxiv_docs:
                all_papers.append({
                    "title": doc.metadata.get("Title", "N/A"),
                    "url": doc.metadata.get("Entry ID", "N/A").replace("http://arxiv.org/abs/", "https://arxiv.org/pdf/"),
                    "content": doc.page_content[:500] if doc.page_content else "No content",
                    "source": "Arxiv"
                })
        except Exception as e:
            print(f"        Error en Arxiv: {str(e)[:100]}")

        # Búsqueda en Semantic Scholar
        try:
            print("      → Buscando en Semantic Scholar...")
            ss_docs = semantic_scholar.load(query=query)
            print(f"        Semantic Scholar: {len(ss_docs)} documentos")
            for doc in ss_docs:
                all_papers.append({
                    "title": doc.get("title", "N/A"),
                    "url": doc.get("url", "N/A"),
                    "content": doc.get("abstract", "No abstract available."),
                    "source": "Semantic Scholar"
                })
        except Exception as e:
            print(f"        Error en Semantic Scholar: {str(e)[:100]}")

    # --- 4. Unificar y eliminar duplicados ---
    print("\n[3/3] Procesando resultados...")
    unique_papers = {paper.get("title", "").lower(): paper for paper in all_papers if paper.get("title") and paper.get("title") != "N/A"}
    final_papers = list(unique_papers.values())
    
    print(f"\n   Total de papers encontrados: {len(all_papers)}")
    print(f"   Papers únicos: {len(final_papers)}")
    
    if final_papers:
        print("\n   Papers encontrados:")
        for idx, paper in enumerate(final_papers[:5], 1):  # Mostrar solo los primeros 5
            print(f"      {idx}. [{paper['source']}] {paper['title'][:60]}...")
    
    message_content = (f"He realizado la investigación académica y encontré {len(final_papers)} artículos relevantes. "
                       "Ahora procederé a generar el reporte de mejoras.")
    if not final_papers:
        message_content = "Realicé la investigación académica pero no encontré artículos relevantes. Esto puede deberse a que las queries no produjeron resultados o hubo errores en las APIs."
    
    print(f"\n{'='*80}")
    print(f"INVESTIGACIÓN ACADÉMICA COMPLETADA: {len(final_papers)} papers")
    print(f"{'='*80}\n")

    return {
        "academic_papers": final_papers,
        "messages": [{"role": "assistant", "content": message_content}]
    }

    
# --- NODO 2: GENERACIÓN DE REPORTE ---
def generate_report(state: ProjectState) -> Dict[str, Any]:
    """
    Genera un reporte de mejoras para el proyecto basado en la investigación académica.
    Incluye automáticamente una propuesta conceptual del proyecto al final.
    """
    print("\n" + "="*80)
    print("NODO: GENERACIÓN DE REPORTE DE MEJORAS")
    print("="*80)
    
    if not state.get("academic_papers"):
        print("   -> No hay investigación académica para generar un reporte. Saltando.")
        return {"improvement_report": "No se pudo generar el reporte ya que no se encontró investigación académica."}

    llm = get_llm()
    
    papers_summary = "\n\n".join(
        [f"Fuente: {p.get('source', 'N/A')}\nTítulo: {p.get('title', '')}\nURL: {p.get('url', '')}\nResumen: {p.get('content', '')}"
         for p in state["academic_papers"]]
    )
    
    # PASO 1: Generar reporte de mejoras con recomendaciones
    print("\n[1/2] Generando reporte de mejoras con recomendaciones...")
    
    recommendations_prompt = ChatPromptTemplate.from_template(
        "Actúa como un consultor de innovación. Redacta un reporte de mejoras para un proyecto, "
        "basándote en los siguientes hallazgos de investigación académica.\n\n"
        "PROYECTO: {project_description}\n\n"
        "HALLAZGOS ACADÉMICOS:\n{papers}\n\n"
        "REPORTE DE MEJORAS:\n"
        "Redacta un reporte con 3 a 5 recomendaciones accionables, explicando cómo se conectan con la investigación."
    )
    
    recommendations_chain = recommendations_prompt | llm
    
    recommendations_response = recommendations_chain.invoke({
        "project_description": state["project_description"],
        "papers": papers_summary
    })
    
    recommendations_content = recommendations_response.content
    print("   Recomendaciones generadas")
    
    # PASO 2: Generar propuesta conceptual integrando las recomendaciones
    print("\n[2/2] Generando propuesta conceptual del proyecto...")
    
    project_title = state.get("project_title", "Proyecto")
    selected_opportunities = state.get("selected_opportunities", [])
    
    opportunities_context = "\n".join([
        f"- {opp.get('origin', 'N/A')}: {opp.get('description', 'N/A')}"
        for opp in selected_opportunities
    ]) if selected_opportunities else "No se seleccionaron oportunidades específicas."
    
    proposal_prompt = ChatPromptTemplate.from_template(
        """Actúa como un consultor de innovación experto. Basándote en el reporte de mejoras que acabas de generar,
        crea una PROPUESTA CONCEPTUAL completa del proyecto que integre todas las recomendaciones.
        
        INFORMACIÓN DEL PROYECTO ORIGINAL:
        Título: {project_title}
        Descripción: {project_description}
        
        OPORTUNIDADES DE FINANCIACIÓN IDENTIFICADAS:
        {opportunities_context}
        
        REPORTE DE MEJORAS Y RECOMENDACIONES:
        {recommendations}
        
        INSTRUCCIONES:
        Genera una propuesta conceptual del proyecto que incluya:
        
        1. **Visión General del Proyecto Mejorado**: Describe qué haría el proyecto de forma clara y concisa
        2. **Objetivos Estratégicos**: Integra los objetivos originales con las recomendaciones del reporte
        3. **Arquitectura Técnica del Sistema**: Describe los componentes principales incorporando las mejoras sugeridas
        4. **Innovaciones Clave**: Destaca las innovaciones que diferencian este proyecto
        5. **Beneficios Esperados**: Cuantifica los beneficios (reducción de costos, eficiencia, sostenibilidad)
        6. **Alineación con Oportunidades de Financiación**: Explica cómo el proyecto se alinea con las oportunidades identificadas
        7. **Roadmap de Implementación**: Sugiere 3-4 fases de implementación
        
        Usa un tono profesional. La propuesta debe ser adecuada para presentarla a inversionistas o en convocatorias.
        
        PROPUESTA CONCEPTUAL DEL PROYECTO:
        """
    )
    
    proposal_chain = proposal_prompt | llm
    
    proposal_response = proposal_chain.invoke({
        "project_title": project_title,
        "project_description": state["project_description"],
        "opportunities_context": opportunities_context,
        "recommendations": recommendations_content
    })
    
    proposal_content = proposal_response.content
    print("   Propuesta conceptual generada")
    
    # COMBINAR REPORTE Y PROPUESTA
    full_report = f"""{recommendations_content}

                {'='*80}
                {'='*80}

                PROPUESTA CONCEPTUAL DEL PROYECTO

                {proposal_content}
            """
    
    print(f"\n{'='*80}")
    print("REPORTE COMPLETO GENERADO")
    print(f"{'='*80}")
    print(f"   Recomendaciones: {len(recommendations_content)} caracteres")
    print(f"   Propuesta conceptual: {len(proposal_content)} caracteres")
    print(f"   Total: {len(full_report)} caracteres\n")
    
    return {
        "improvement_report": full_report,
        "messages": [{
            "role": "assistant",
            "content": f"He finalizado el reporte de mejoras con la propuesta conceptual integrada. Ahora puedes hacer preguntas sobre el proyecto, las oportunidades o el reporte.\n\n--- REPORTE COMPLETO ---\n{full_report[:500]}..."
        }]
    }