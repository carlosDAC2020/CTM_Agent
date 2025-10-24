# src/agent/nodes/analysis.py


from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from datetime import datetime

# Importaciones para herramientas académicas
from langchain_community.retrievers import ArxivRetriever
from langchain_community.utilities.semanticscholar import SemanticScholarAPIWrapper

from ..state import ProjectState
from ..config import get_llm

# ============================================================================
# MODELOS DE DATOS Y LÓGICA COMPARTIDA
# ============================================================================

class AcademicQueries(BaseModel):
    """Define la estructura para las queries de búsqueda académica."""
    queries: List[str] = Field(description="Lista de 3 queries de búsqueda para papers académicos")

# ============================================================================
# NODO 1: GENERADOR DE QUERIES ACADÉMICAS
# ============================================================================

def generate_academic_queries_node(state: ProjectState) -> Dict[str, Any]:
    """
    NODO: Genera las queries iniciales para la investigación de Estado del Arte.
    Este es el primer paso del nuevo flujo principal.
    """
    print("\n" + "="*80)
    print("NODO: Generando Queries de Búsqueda Académica (Estado del Arte)")
    print("="*80)

    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=AcademicQueries)
    
    system_prompt = """
    Eres un asistente de investigación. Basado en la descripción de un proyecto, 
    genera 3 queries de búsqueda efectivas y concisas en inglés para encontrar 
    papers sobre el marco teórico y el estado del arte en ArXiv y Semantic Scholar.
    Enfócate en los aspectos técnicos y científicos clave.
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Título del Proyecto: {project_title}\nDescripción: {project_description}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        response = chain.invoke({
            "project_title": state["project_title"],
            "project_description": state["project_description"],
            "format_instructions": parser.get_format_instructions()
        })
        search_queries = response.get('queries', [])
        print(f"   -> Queries académicas generadas: {search_queries}")
        return {"search_queries": search_queries}
    except Exception as e:
        print(f"   ⚠️ Error generando queries académicas: {e}")
        return {"search_queries": []}

# ============================================================================
# NODO 2: EJECUTOR DE BÚSQUEDA ACADÉMICA
# ============================================================================

def academic_research(state: ProjectState) -> Dict[str, Any]:
    """
    NODO: Ejecuta las búsquedas en Arxiv y Semantic Scholar usando las queries del estado.
    Acumula los resultados y evita duplicados.
    """
    print("\n" + "="*80)
    print("NODO: Ejecutando Búsqueda Académica (Con Memoria)")
    print("="*80)
    
    search_queries = state.get("search_queries")
    if not search_queries:
        print("   -> No hay queries de búsqueda. Saltando este paso.")
        return {}
    
    print(f"   -> Ejecutando {len(search_queries)} queries de búsqueda...")
    
    # --- Inicializar herramientas ---
    try:
        arxiv_retriever = ArxivRetriever(load_max_docs=3, doc_content_chars_max=1500)
        semantic_scholar = SemanticScholarAPIWrapper(top_k_results=3)
    except Exception as e:
        print(f"   ⚠️ Error inicializando herramientas de búsqueda: {e}")
        return {}

    # --- Ejecutar búsquedas ---
    newly_found_papers = []
    for query in search_queries:
        try: # Arxiv
            arxiv_docs = arxiv_retriever.invoke(query)
            for doc in arxiv_docs:
                newly_found_papers.append({
                    "title": doc.metadata.get("Title", "N/A"),
                    "url": doc.metadata.get("Entry ID", "N/A").replace("http://arxiv.org/abs/", "https://arxiv.org/pdf/"),
                    "content": doc.page_content, "source": "Arxiv"
                })
        except Exception as e:
            print(f"        Error en Arxiv para query '{query}': {e}")

        try: # Semantic Scholar
            ss_docs = semantic_scholar.run(query)
            if isinstance(ss_docs, list):
                for doc in ss_docs:
                    newly_found_papers.append({
                        "title": doc.get("title", "N/A"),
                        "url": doc.get("url", "N/A"),
                        "content": doc.get("abstract", "No abstract."), "source": "Semantic Scholar"
                    })
        except Exception as e:
            print(f"        Error en Semantic Scholar para query '{query}': {e}")

    # --- Acumular y Desduplicar Resultados ---
    existing_papers = state.get("academic_papers", [])
    combined_papers = existing_papers + newly_found_papers
    
    unique_papers_dict = {
        paper.get("title", "").lower().strip(): paper 
        for paper in combined_papers if paper.get("title", "N/A") != "N/A"
    }
    final_papers_list = list(unique_papers_dict.values())
    
    newly_added_count = len(final_papers_list) - len(existing_papers)
    print(f"   -> Se añadieron {newly_added_count} papers únicos. Total en colección: {len(final_papers_list)}")
    
    message = f"He realizado la investigación y acumulado un total de {len(final_papers_list)} artículos. Ahora generaré el reporte de Marco Teórico."
    
    return {
        "academic_papers": final_papers_list,
        "messages": [{"role": "assistant", "content": message}]
    }

# ============================================================================
# NODO 3: GENERADOR DE REPORTE DE ESTADO DEL ARTE
# ============================================================================

def generate_state_of_the_art_report(state: ProjectState) -> Dict[str, Any]:
    """
    Genera un reporte académico que establece el marco teórico y el estado del arte
    del proyecto, basándose en la investigación académica proporcionada.
    """
    print("\n" + "="*80)
    print("NODO: GENERACIÓN DE REPORTE ACADÉMICO (MARCO TEÓRICO Y ESTADO DEL ARTE)")
    print("="*80)
    
    if not state.get("academic_papers"):
        print("   -> No hay investigación académica para generar un reporte. Saltando.")
        return {"improvement_report": "No se pudo generar el reporte ya que no se encontró investigación académica."}

    llm = get_llm()
    
    # Prepara un resumen de los papers que servirá como contexto principal para el LLM.
    papers_summary = "\n\n".join(
        [f"Fuente: {p.get('source', 'N/A')}\nTítulo: {p.get('title', '')}\nURL: {p.get('url', '')}\nResumen: {p.get('content', '')}"
         for p in state["academic_papers"]]
    )
    
    print("\n[1/1] Generando reporte de Marco Teórico y Estado del Arte...")
    
    academic_report_prompt = ChatPromptTemplate.from_template(
        """
        **Rol:** Eres un Investigador Senior y Analista Científico con alta especialización en la redacción de documentos técnicos (whitepapers) y secciones de introducción para artículos de investigación (papers).

        **Tarea:** Redactar un reporte de fundamentación exhaustivo para un proyecto tecnológico. Tu reporte debe sintetizar la investigación académica proporcionada para construir un sólido **Marco Teórico** y un detallado **Análisis del Estado del Arte**. El objetivo es crear un documento fundacional que justifique la relevancia y la innovación del proyecto.

        **Contexto del Proyecto:**
        - Título: {project_title}
        - Descripción: {project_description}

        **Fuentes de Investigación Primarias (Resúmenes de Artículos Académicos):**
        {papers}

        **INSTRUCCIONES DE ALTO NIVEL:**
        Genera un reporte coherente y bien estructurado que siga rigurosamente el siguiente formato. Sé analítico, profundo y conecta siempre la teoría con el proyecto específico.

        ---
        
        ## 1. Marco Teórico

        ### 1.1. Conceptos Fundamentales
        Define los 3-4 conceptos teóricos más cruciales que sustentan este proyecto, basándote en la literatura proporcionada. Para cada concepto, ofrece una explicación clara y su relevancia directa para el problema que {project_title} busca resolver.

        ### 1.2. Modelos y Metodologías Relevantes
        Describe los modelos (matemáticos, computacionales, etc.), algoritmos o metodologías científicas clave que aparecen en la investigación. No te limites a enumerarlos; explica su funcionamiento a un nivel conceptual y por qué son la base sobre la que se puede construir la solución del proyecto.
        
        ### 1.3. Justificación Científica del Enfoque del Proyecto
        Sintetiza cómo la combinación de los conceptos y modelos anteriores valida el enfoque descrito para el proyecto. Este apartado debe responder a la pregunta: ¿Por qué, desde un punto de vista científico y teórico, es viable y prometedor el camino que propone este proyecto?

        ---
        
        ## 2. Análisis del Estado del Arte

        ### 2.1. Técnicas y Enfoques Predominantes
        Basándote exclusivamente en los papers, resume las soluciones, arquitecturas y tecnologías que se emplean actualmente para abordar el problema central del proyecto. Agrupa enfoques similares si es posible.
        
        ### 2.2. Limitaciones Identificadas y Brechas en la Investigación
        Identifica y detalla los desafíos no resueltos, las limitaciones de los métodos actuales o las "brechas" (gaps) que la propia investigación académica señala. Sé específico. Por ejemplo: "baja precisión en condiciones de poca luz", "alto coste computacional", "falta de datasets estandarizados", etc.

        ### 2.3. Posicionamiento e Innovación Clave del Proyecto
        Este es el punto más importante. Explica de forma precisa cómo {project_title} se posiciona frente al estado del arte. Argumenta cuál de las limitaciones identificadas en el punto anterior aborda directamente. Define su principal propuesta de valor innovadora en el contexto de la investigación actual.

        ---

        **REQUISITOS ADICIONALES:**
        - **Lenguaje:** Utiliza un tono formal, objetivo y académico.
        - **Citas:** Cuando un hallazgo o concepto provenga de una fuente específica, referéncialo sutilmente en el texto. Ejemplo: "...tal como se demuestra en el estudio sobre Fusión de Sensores (Fuente: [Nombre de la Fuente], Título: [Título del Paper])".
        - **Formato:** Usa formato Markdown (`##`, `###`, `**`, `-`) para garantizar una estructura limpia y legible.

        **COMIENZA EL REPORTE A CONTINUACIÓN:**
        """
    )
    
    report_chain = academic_report_prompt | llm
    report_response = report_chain.invoke({
        "project_title": state["project_title"],
        "project_description": state["project_description"],
        "papers": papers_summary
    })
    academic_content = report_response.content
    print("   -> Reporte académico completo generado.")
    
    # --- ENSAMBLAJE FINAL DEL REPORTE ---
    current_date = datetime.now().strftime("%d de %B de %Y")
    academic_sources = "\n".join([f"- [{p.get('source', 'N/A')}] {p.get('title', 'N/A')}\n  URL: {p.get('url', 'No disponible')}" for p in state.get("academic_papers", [])])
    #web_sources = "\n".join([f"- {res.get('title', 'N/A')}\n  URL: {res.get('url', 'No disponible')}" for res in state.get("relevant_results", [])])

    full_report = f"""
# Reporte de Fundamentación y Estado del Arte

**Proyecto:** {state.get('project_title', 'N/A')}
**Fecha de Generación:** {current_date}

---

{academic_content}

---
## 3. Fuentes y Referencias

### Artículos Académicos Consultados
{academic_sources if academic_sources else "No se encontraron artículos académicos."}


"""

### Fuentes Web Relevantes
#{web_sources if web_sources else "No se encontraron fuentes web relevantes."}
    
    print(f"\n{'='*80}")
    print("REPORTE COMPLETO GENERADO Y FORMATEADO")
    print(f"{'='*80}\n")
    
    return {
        "improvement_report": full_report,
        "report_type": "general",  
        "messages": [{
            "role": "assistant",
            "content": "He finalizado el reporte de fundamentación, incluyendo el marco teórico y el estado del arte. Ahora procederé a guardarlo como un archivo PDF."
        }]
    }


# ============================================================================
# NODO PARA REPORTE ESPECÍFICO
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