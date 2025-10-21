# src/agent/nodes/analysis.py

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from datetime import datetime

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
    Busca papers académicos relevantes y los AÑADE a la lista existente,
    evitando duplicados.
    """
    print("\n" + "="*80)
    print("NODO: INVESTIGACIÓN ACADÉMICA (Con Memoria)")
    print("="*80)
    
    selected_opportunities = state.get("selected_opportunities")
    if not selected_opportunities:
        print("   -> No hay oportunidades seleccionadas. Saltando este paso.")
        # Retornamos un diccionario vacío para no modificar el estado existente.
        return {}
    
    print(f"\n   Analizando {len(selected_opportunities)} oportunidades seleccionadas...")
        
    llm = get_llm()
    
    # --- 1. Inicializar las herramientas especializadas ---
    print("   -> Inicializando herramientas: Arxiv, Semantic Scholar")
    try:
        arxiv_retriever = ArxivRetriever(load_max_docs=2, doc_content_chars_max=1000)
        semantic_scholar = SemanticScholarAPIWrapper(top_k_results=3)
    except Exception as e:
        print(f"   Error inicializando herramientas: {e}")
        return {}

    # --- 2. Generar múltiples queries de búsqueda ---
    # (Esta sección de tu código ya es correcta)
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
    except Exception as e:
        print(f"   Error generando queries académicas: {e}")
        return {}

    # --- 3. Ejecutar búsquedas en ambas herramientas ---
    print("\n[2/3] Buscando papers académicos...")
    newly_found_papers = [] # Usamos una nueva lista para los hallazgos de esta ronda
    
    for idx, query in enumerate(search_queries, 1):
        print(f"\n   Query {idx}/{len(search_queries)}: '{query[:60]}...'")
        
        # Búsqueda en Arxiv
        try:
            print("      → Buscando en Arxiv...")
            arxiv_docs = arxiv_retriever.invoke(query)
            print(f"        Arxiv: {len(arxiv_docs)} documentos")
            for doc in arxiv_docs:
                newly_found_papers.append({
                    "title": doc.metadata.get("Title", "N/A"),
                    "url": doc.metadata.get("Entry ID", "N/A").replace("http://arxiv.org/abs/", "https://arxiv.org/pdf/"),
                    "content": doc.page_content[:500] if doc.page_content else "No content",
                    "source": "Arxiv"
                })
        except Exception as e:
            print(f"        Error en Arxiv: {str(e)[:100]}")

        # Búsqueda en Semantic Scholar (Corregido a .run)
        try:
            print("      → Buscando en Semantic Scholar...")
            # Usamos .run() que es más estándar para las herramientas LangChain
            ss_docs = semantic_scholar.run(query)
            # La salida de .run() puede variar, asumimos que devuelve una lista de diccionarios
            if isinstance(ss_docs, list):
                print(f"        Semantic Scholar: {len(ss_docs)} documentos")
                for doc in ss_docs:
                    newly_found_papers.append({
                        "title": doc.get("title", "N/A"),
                        "url": doc.get("url", "N/A"),
                        "content": doc.get("abstract", "No abstract available."),
                        "source": "Semantic Scholar"
                    })
        except Exception as e:
            print(f"        Error en Semantic Scholar: {str(e)[:100]}")

    # --- 4. ACUMULAR, UNIFICAR Y ELIMINAR DUPLICADOS ---
    print("\n[3/3] Procesando y acumulando resultados...")
    
    # Obtenemos los papers que ya existían en el estado (con un valor por defecto seguro)
    existing_papers = state.get("academic_papers", [])
    print(f"   -> Papers existentes en el estado: {len(existing_papers)}")
    
    # Combinamos la lista existente con los nuevos hallazgos de esta búsqueda
    combined_papers = existing_papers + newly_found_papers
    
    # Aplicamos la lógica de desduplicación sobre la lista COMPLETA
    unique_papers_dict = {
        paper.get("title", "").lower().strip(): paper 
        for paper in combined_papers if paper.get("title") and paper.get("title", "N/A") != "N/A"
    }
    final_papers_list = list(unique_papers_dict.values())
    
    newly_added_count = len(final_papers_list) - len(existing_papers)
    
    print(f"\n   Total de papers encontrados en esta búsqueda: {len(newly_found_papers)}")
    print(f"   Se añadieron {newly_added_count} papers únicos a la colección.")
    print(f"   Total de papers acumulados: {len(final_papers_list)}")
    
    if final_papers_list:
        print("\n   Colección actual de papers (primeros 5):")
        for idx, paper in enumerate(final_papers_list[:5], 1):
            print(f"      {idx}. [{paper.get('source', 'N/A')}] {paper.get('title', 'N/A')[:60]}...")
    
    message_content = (f"He realizado la investigación académica y añadido {newly_added_count} artículos nuevos, "
                       f"para un total de {len(final_papers_list)} en la colección. "
                       "Ahora procederé a generar el reporte de mejoras.")
    if newly_added_count == 0 and not final_papers_list:
        message_content = "No encontré nuevos artículos académicos relevantes en esta búsqueda."
    
    print(f"\n{'='*80}")
    print(f"INVESTIGACIÓN ACADÉMICA COMPLETADA: {len(final_papers_list)} papers totales")
    print(f"{'='*80}\n")

    return {
        "academic_papers": final_papers_list,
        "messages": [{"role": "assistant", "content": message_content}]
    }

    
# --- NODO 2: GENERACIÓN DE REPORTE ---
def generate_report(state: ProjectState) -> Dict[str, Any]:
    """
    Genera un reporte de mejoras y una propuesta conceptual con prompts
    altamente detallados para una salida de calidad profesional.
    """
    print("\n" + "="*80)
    print("NODO: GENERACIÓN DE REPORTE DE MEJORAS (AVANZADO)")
    print("="*80)
    
    if not state.get("academic_papers"):
        print("   -> No hay investigación académica para generar un reporte. Saltando.")
        return {"improvement_report": "No se pudo generar el reporte ya que no se encontró investigación académica."}

    llm = get_llm()
    
    papers_summary = "\n\n".join(
        [f"Fuente: {p.get('source', 'N/A')}\nTítulo: {p.get('title', '')}\nURL: {p.get('url', '')}\nResumen: {p.get('content', '')}"
         for p in state["academic_papers"]]
    )
    
    # ============================================================================
    # PASO 1: PROMPT MEJORADO PARA EL REPORTE DE RECOMENDACIONES
    # ============================================================================
    print("\n[1/2] Generando reporte de mejoras con recomendaciones...")
    
    recommendations_prompt = ChatPromptTemplate.from_template(
        """
        **Rol:** Eres un Consultor Senior de Innovación y Estrategia Tecnológica.

        **Tarea:** Redactar un reporte de mejoras directivo y accionable para un proyecto tecnológico, basándote en hallazgos de investigación académica. El objetivo es proporcionar valor tangible y guiar al equipo de desarrollo.

        **Contexto del Proyecto:**
        - Título: {project_title}
        - Descripción: {project_description}

        **Contexto de la Investigación (Hallazgos Académicos):**
        {papers}

        **INSTRUCCIONES CLAVE:**
        1.  Redacta una **Introducción Ejecutiva** breve que resuma el propósito del reporte.
        2.  Desarrolla **3 recomendaciones principales**. No más, no menos.
        3.  **Para CADA recomendación, sigue ESTRICTAMENTE el siguiente formato de 4 puntos:**
            - **### Título de la Recomendación:** Un título claro y conciso (ej: "Implementación de Fusión de Sensores para Robustez Ambiental").
            - **- Descripción:** Explica en qué consiste la mejora propuesta.
            - **- Justificación y Conexión con la Investigación:** Detalla por qué esta mejora es crucial, citando explícitamente los hallazgos de los papers que la respaldan. Usa el formato `(Fuente: [Nombre de la Fuente], Título: [Título del Paper])`.
            - **- Pasos de Acción Sugeridos:** Enumera 2-3 pasos concretos y prácticos que el equipo puede tomar para implementar la recomendación.
        4.  Finaliza con una **Conclusión y Próximos Pasos** que resuma el impacto de las mejoras.
        5.  Usa un lenguaje formal, claro y directivo. Utiliza formato Markdown (`##`, `###`, `**`, `-`) para la estructura.

        **COMIENZA EL REPORTE DE MEJORAS A CONTINUACIÓN:**
        """
    )
    
    recommendations_chain = recommendations_prompt | llm
    recommendations_response = recommendations_chain.invoke({
        "project_title": state["project_title"],
        "project_description": state["project_description"],
        "papers": papers_summary
    })
    recommendations_content = recommendations_response.content
    print("   Recomendaciones generadas")
    
    # ============================================================================
    # PASO 2: PROMPT MEJORADO PARA LA PROPUESTA CONCEPTUAL
    # ============================================================================
    print("\n[2/2] Generando propuesta conceptual del proyecto...")
    
    project_title = state.get("project_title", "Proyecto")
    selected_opportunities = state.get("selected_opportunities", [])
    opportunities_context = "\n".join([
        f"- {opp.get('origin', 'N/A')}: {opp.get('description', 'N/A')}"
        for opp in selected_opportunities
    ]) if selected_opportunities else "No se seleccionaron oportunidades específicas."
    
    proposal_prompt = ChatPromptTemplate.from_template(
        """
        **Rol:** Eres un Director de Estrategia e Innovación, experto en la redacción de propuestas de financiación para proyectos de alta tecnología (Deep Tech).

        **Audiencia:** Tu escrito será leído por inversionistas de capital de riesgo, comités de evaluación de subvenciones gubernamentales y socios estratégicos.

        **Tarea:** Transformar un reporte técnico de mejoras en una **Propuesta Conceptual** completa, convincente y orientada a resultados.

        **MATERIAL DE ORIGEN:**
        1.  **Información del Proyecto Original:**
            - Título: {project_title}
            - Descripción: {project_description}
        2.  **Oportunidades de Financiación Identificadas:**
            {opportunities_context}
        3.  **Reporte de Mejoras y Recomendaciones Técnicas (que acabas de generar):**
            {recommendations}

        **INSTRUCCIONES DETALLADAS PARA LA PROPUESTA:**
        Genera una propuesta conceptual que siga esta estructura rigurosa. Sé detallado y convincente en cada sección:

        1.  **Visión General del Proyecto Mejorado (Elevator Pitch):** En un párrafo conciso, describe el problema que se resuelve, la solución innovadora propuesta (integrando las recomendaciones) y el impacto esperado.
        2.  **Objetivos Estratégicos (Formato SMART):** Define 3-4 objetivos claros, medibles y con un plazo definido (ej: "Reducir los falsos positivos en un 40% en 18 meses...").
        3.  **Arquitectura Técnica del Sistema:** Describe los componentes principales de forma detallada, dividiéndolos en:
            - **Componentes de Hardware:** (ej: Drones, tipo de sensores, hardware de computación en el borde).
            - **Plataforma de Software/Nube:** (ej: Centro de control, base de datos, API, dashboard de visualización).
            - **Motor de Inteligencia Artificial:** Explica los modelos clave que se usarán, basándote en las recomendaciones (ej: "Modelo de Fusión de Datos SAR-Óptico", "Clasificador Basado en Few-Shot Learning").
        4.  **Innovaciones Clave y Ventaja Competitiva:** Destaca 2-3 innovaciones que hacen a este proyecto único. Explica por qué es difícil de replicar (su "foso competitivo").
        5.  **Beneficios Esperados y KPIs:** Cuantifica los beneficios. Usa métricas y KPIs (Key Performance Indicators) claros. (ej: "Reducción de costos de monitoreo en un 30%", "Aumento de la cobertura operativa en un 50% en temporada de lluvias", "Tiempo de detección reducido de semanas a horas").
        6.  **Alineación Estratégica con Oportunidades de Financiación:** Para cada oportunidad identificada, escribe un párrafo explicando explícitamente cómo este proyecto mejorado cumple con sus requisitos y objetivos. Sé directo: "Para la oportunidad X, nuestro enfoque en [innovación clave] aborda directamente su objetivo de [objetivo de la oportunidad]".
        7.  **Roadmap de Implementación por Fases:** Propón un plan de 3-4 fases con duraciones estimadas y entregables clave para cada una. (ej: "Fase 1 (Meses 1-6): Prototipado de Modelos IA y Selección de Hardware...").

        Usa un tono profesional, convincente y basado en datos. Evita la jerga vaga. Utiliza formato Markdown (`##`, `###`, `**`, `-`) para la estructura.

        **COMIENZA LA PROPUESTA CONCEPTUAL DEL PROYECTO A CONTINUACIÓN:**
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
    
    # --- ENSAMBLAJE FINAL DEL REPORTE (sin cambios en la lógica) ---
    current_date = datetime.now().strftime("%d de %B de %Y")
    academic_sources = "\n".join([f"- [{p.get('source', 'N/A')}] {p.get('title', 'N/A')}\n  URL: {p.get('url', 'No disponible')}" for p in state.get("academic_papers", [])])
    web_sources = "\n".join([f"- {res.get('title', 'N/A')}\n  URL: {res.get('url', 'No disponible')}" for res in state.get("relevant_results", [])])

    full_report = f"""
# PROPUESTA CONCEPTUAL Y REPORTE DE MEJORAS

**Proyecto:** {state.get('project_title', 'N/A')}
**Fecha de Generación:** {current_date}

---
## 1. Reporte de Mejoras y Recomendaciones

{recommendations_content}

---
## 2. Propuesta Conceptual del Proyecto Mejorado

{proposal_content}

---
## 3. Fuentes y Referencias

### Artículos Académicos Consultados
{academic_sources if academic_sources else "No se encontraron artículos académicos."}

### Fuentes Web Relevantes
{web_sources if web_sources else "No se encontraron fuentes web relevantes."}
"""
    
    print(f"\n{'='*80}")
    print("REPORTE COMPLETO GENERADO Y FORMATEADO (CON PROMPTS MEJORADOS)")
    print(f"{'='*80}\n")
    
    return {
        "improvement_report": full_report,
        "report_type": "general",
        "messages": [{
            "role": "assistant",
            "content": "He finalizado el reporte de mejoras y la propuesta conceptual. Ahora procederé a guardarlo como un archivo PDF."
        }]
    }


# ============================================================================
# NODO DUMMY PARA REPORTE ESPECÍFICO
# ============================================================================
def generate_specific_report(state: ProjectState) -> Dict[str, Any]:
    """
    Genera un reporte detallado para una ÚNICA oportunidad seleccionada.
    """
    print("\n" + "="*80)
    print("NODO: Generar Reporte Específico")
    print("="*80)

    llm = get_llm()
    opportunity_index = state.get("action_input")
    
    try:
        # Obtener la oportunidad específica del estado
        opportunity = state["investment_opportunities"][opportunity_index]
        opportunity_details = f"Origen: {opportunity['origin']}\nDescripción: {opportunity['description']}"
    except (TypeError, IndexError):
        return {
            "messages": [{"role": "assistant", "content": "No pude encontrar la oportunidad solicitada. Por favor, verifica el índice."}],
            "next_action": "continue"
        }

    print(f"   -> Generando reporte para la oportunidad con índice: {opportunity_index}")

    # Prompt para generar el reporte específico
    specific_report_prompt = ChatPromptTemplate.from_template(
        """
        Actúa como un consultor estratégico. Tu tarea es generar un reporte de análisis y recomendaciones
        para alinear un proyecto tecnológico con una oportunidad de financiación específica.

        **PROYECTO:**
        Título: {project_title}
        Descripción: {project_description}

        **OPORTUNIDAD DE FINANCIACIÓN A ANALIZAR:**
        {opportunity_details}

        **HALLAZGOS DE INVESTIGACIÓN ACADÉMICA (Contexto):**
        {papers_summary}

        **INSTRUCCIONES PARA EL REPORTE:**
        Genera un reporte conciso que incluya los siguientes puntos:
        1.  **Análisis de Alineación:** Evalúa qué tan bien encaja el proyecto con los objetivos y requisitos de la oportunidad. Destaca las sinergias.
        2.  **Recomendaciones de Adaptación:** Sugiere 2-3 modificaciones o puntos clave a enfatizar en la propuesta del proyecto para maximizar las posibilidades de éxito con esta financiación. Conecta tus sugerencias con la investigación académica.
        3.  **Borrador de Pitch:** Escribe un párrafo breve (pitch) que se podría usar en la aplicación, explicando por qué este proyecto es el candidato ideal para esta oportunidad.

        Usa un tono profesional y directo.
        """
    )
    
    papers_summary = "\n".join([f"- {p['title']}" for p in state.get("academic_papers", [])])
    
    chain = specific_report_prompt | llm
    
    report_content = chain.invoke({
        "project_title": state["project_title"],
        "project_description": state["project_description"],
        "opportunity_details": opportunity_details,
        "papers_summary": papers_summary
    }).content

    # Añadimos un encabezado al reporte para guardarlo como PDF
    current_date = datetime.now().strftime("%d de %B de %Y")
    full_specific_report = f"""
# ANÁLISIS DE OPORTUNIDAD ESPECÍFICA

**Proyecto:** {state['project_title']}
**Oportunidad Analizada:** {opportunity['origin']}
**Fecha de Generación:** {current_date}

---
{report_content}
"""

    return {
        "improvement_report": full_specific_report, 
        "report_type": "specific",
        "messages": [{"role": "assistant", "content": f"He generado el análisis para la oportunidad {opportunity_index}. Procederé a guardarlo como PDF."}],
        "next_action": "continue",
        "action_input": None
    }