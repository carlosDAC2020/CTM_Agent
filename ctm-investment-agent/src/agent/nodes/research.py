# src/agent/nodes/research.py

import os
import time
from typing import Dict, Any, List
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from tavily import TavilyClient
try:
    from langchain_community.tools import BraveSearch
    BRAVE_AVAILABLE = True
except ImportError:
    BRAVE_AVAILABLE = False

from ..state import ProjectState
from ..config import get_llm


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class SearchQuery(BaseModel):
    """Modelo para una query de búsqueda."""
    idea: str = Field(description="La idea o el enfoque principal de la búsqueda.")
    international_query: str = Field(description="Query para oportunidades internacionales (en inglés).")
    national_query: str = Field(description="Query para oportunidades nacionales en Colombia (en español).")


class QueryList(BaseModel):
    """Lista de queries de búsqueda."""
    queries: List[SearchQuery] = Field(description="Lista de 5 pares de queries de búsqueda.")


class ScrutinyResult(BaseModel):
    """Resultado del análisis de relevancia de una fuente."""
    is_relevant: bool = Field(description="True si la fuente es una convocatoria o página de financiación directa.")


class FundingOpportunity(BaseModel):
    """Modelo para una oportunidad de financiación."""
    origin: str = Field(description="Nombre de la organización que ofrece la financiación.")
    description: str = Field(description="Resumen de la oportunidad de financiación.")
    financing_type: str = Field(default="", description="Tipo de financiación (grant, inversión, subsidio).")
    main_requirements: List[str] = Field(default_factory=list, description="Requisitos principales.")
    application_deadline: str = Field(default="", description="Fecha límite (YYYY-MM-DD).")
    opportunity_url: str = Field(default="", description="URL de la convocatoria.")


class FundingOpportunityList(BaseModel):
    """Lista de oportunidades de financiación."""
    opportunities: List[FundingOpportunity] = Field(description="Lista de oportunidades encontradas.")


# ============================================================================
# PASO 1: GENERACIÓN DE QUERIES
# ============================================================================

def generate_search_queries(project_details: str, llm) -> List[str]:
    """
    Genera queries de búsqueda estratégicas basadas en la descripción del proyecto.
    
    Returns:
        Lista de strings con queries de búsqueda
    """
    print("\n[1/4] Generando queries de búsqueda...")
    
    system_prompt = """
    Actúa como un experto en la búsqueda de financiación para proyectos de innovación y tecnología. 
    Tu tarea es generar consultas de búsqueda (queries) estratégicas para encontrar oportunidades 
    de financiación (grants, funding, convocatorias, etc.) basadas en la descripción del proyecto.
    
    Debes analizar el título, la descripción y las palabras clave del proyecto para crear 5 ideas 
    de búsqueda diferentes y efectivas.
    
    Por cada idea, genera dos versiones de la query:
    1. Una para búsquedas internacionales, en inglés.
    2. Una para búsquedas a nivel nacional (Colombia), en español.
    
    Utiliza sinónimos y términos relacionados como "funding", "grants", "convocatorias", 
    "financiación", "proyectos de investigación", "venture capital", etc.
    
    {format_instructions}
    """
    
    parser = JsonOutputParser(pydantic_object=QueryList)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{project_details}"),
    ])
    
    chain = prompt_template | llm | parser
    
    try:
        result = chain.invoke({
            "project_details": project_details,
            "format_instructions": parser.get_format_instructions()
        })
        
        queries = result.get("queries", [])
        print(f"   ✅ Generadas {len(queries)} ideas de búsqueda")
        
        # Aplanamos las queries (internacional y nacional)
        flat_queries = []
        for q in queries:
            flat_queries.append(q.get("international_query"))
            flat_queries.append(q.get("national_query"))
        
        return flat_queries
        
    except Exception as e:
        print(f"   ⚠️ Error generando queries: {e}")
        return []


# ============================================================================
# PASO 2: BÚSQUEDA WEB
# ============================================================================

def search_web(queries: List[str]) -> List[Dict]:
    """
    Realiza búsquedas web usando Tavily API y opcionalmente Brave Search.
    
    Returns:
        Lista de resultados de búsqueda normalizados
    """
    print(f"\n[2/4] Buscando en la web ({len(queries)} queries)...")
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    
    if not tavily_api_key and not brave_api_key:
        print("   ⚠️ Ni TAVILY_API_KEY ni BRAVE_SEARCH_API_KEY configuradas")
        return []
    
    all_results = []
    
    # Inicializar clientes
    tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None
    brave_client = None
    if brave_api_key and BRAVE_AVAILABLE:
        try:
            brave_client = BraveSearch.from_api_key(
                api_key=brave_api_key,
                search_kwargs={"count": 2}
            )
        except Exception as e:
            print(f"   ⚠️ Error inicializando Brave Search: {e}")
    
    for idx, query in enumerate(queries, 1):
        print(f"   -> Query {idx}/{len(queries)}: {query[:60]}...")
        
        # Buscar con Tavily
        if tavily_client:
            try:
                response = tavily_client.search(query=query, max_results=2)
                for result in response.get("results", []):
                    all_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0),
                        "source": "tavily"
                    })
            except Exception as e:
                print(f"      ⚠️ Error en Tavily: {e}")
        
        # Buscar con Brave
        if brave_client:
            try:
                brave_results = brave_client.run(query)
                # Brave devuelve un string, necesitamos parsearlo
                if isinstance(brave_results, str):
                    # Extraer información básica del string
                    all_results.append({
                        "title": f"Brave Search: {query[:40]}",
                        "url": "",
                        "content": brave_results[:500],
                        "score": 0.5,
                        "source": "brave"
                    })
            except Exception as e:
                print(f"      ⚠️ Error en Brave: {e}")
        
        time.sleep(1)  # Pausa entre búsquedas
    
    print(f"   ✅ Encontrados {len(all_results)} resultados")
    if tavily_client:
        print(f"      - Tavily habilitado")
    if brave_client:
        print(f"      - Brave Search habilitado")
    
    return all_results


# ============================================================================
# PASO 3: ESCRUTINIO (FILTRADO DE RELEVANCIA)
# ============================================================================

def scrutinize_results(search_results: List[Dict], llm) -> List[Dict]:
    """
    Filtra los resultados de búsqueda para quedarse solo con fuentes relevantes.
    
    Returns:
        Lista de resultados relevantes
    """
    print(f"\n[3/4] Escrutando {len(search_results)} resultados...")
    
    system_prompt = """
    Eres un experto en identificar fuentes de financiación legítimas.
    
    Tu tarea es determinar si el contenido proporcionado corresponde a:
    - Una convocatoria de financiación activa
    - Una página oficial de grants o funding
    - Un programa de inversión o subsidio
    
    NO son relevantes:
    - Noticias sobre financiación
    - Blogs o artículos de opinión
    - Directorios o listados generales
    - Artículos académicos
    
    Analiza el título y el contenido y responde si es relevante.
    
    {format_instructions}
    """
    
    parser = JsonOutputParser(pydantic_object=ScrutinyResult)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Título: {title}\n\nContenido: {content}\n\nURL: {url}"),
    ])
    
    chain = prompt_template | llm | parser
    
    relevant_results = []
    
    for result in search_results:
        try:
            scrutiny = chain.invoke({
                "title": result.get("title", ""),
                "content": result.get("content", "")[:500],  # Limitamos el contenido
                "url": result.get("url", ""),
                "format_instructions": parser.get_format_instructions()
            })
            
            if scrutiny.get("is_relevant", False):
                print(f"   ✅ Relevante: {result.get('title', '')[:60]}")
                relevant_results.append(result)
            else:
                print(f"   ❌ Descartado: {result.get('title', '')[:60]}")
            
            time.sleep(4.1)  # Respetamos límite de API (15 RPM)
            
        except Exception as e:
            print(f"   ⚠️ Error en escrutinio: {e}")
            continue
    
    print(f"   ✅ Resultados relevantes: {len(relevant_results)}/{len(search_results)}")
    return relevant_results


# ============================================================================
# PASO 4: EXTRACCIÓN DE OPORTUNIDADES
# ============================================================================

def extract_opportunities(relevant_results: List[Dict], llm) -> List[Dict]:
    """
    Extrae información estructurada de oportunidades de las fuentes relevantes.
    
    Returns:
        Lista de diccionarios con oportunidades de financiación
    """
    print(f"\n[4/4] Extrayendo oportunidades de {len(relevant_results)} fuentes...")
    
    # Obtener fecha actual para filtrar oportunidades vigentes
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    system_prompt = """
    Eres un experto en analizar convocatorias de financiación.
    
    IMPORTANTE: La fecha actual es {current_date}. Solo debes extraer oportunidades que estén VIGENTES, 
    es decir, cuya fecha límite (deadline) sea POSTERIOR a la fecha actual. 
    NO incluyas oportunidades vencidas o cerradas.
    
    Tu tarea es extraer TODAS las oportunidades de financiación VIGENTES mencionadas en el contenido.
    Para cada oportunidad, identifica:
    - Nombre de la organización que ofrece la financiación
    - Descripción concisa de la oportunidad
    - Tipo de financiación (grant, inversión, subsidio, etc.)
    - Requisitos principales para aplicar
    - Fecha límite de aplicación (formato YYYY-MM-DD si está disponible)
    - URL específica de la convocatoria
    
    REGLAS IMPORTANTES:
    1. Si encuentras una fecha límite, verifica que sea posterior a {current_date}
    2. Si no hay fecha límite explícita pero el contenido indica que está "abierta" o "vigente", inclúyela
    3. Si el contenido dice "cerrada", "vencida" o tiene fecha anterior a {current_date}, NO la incluyas
    4. Si el contenido menciona múltiples oportunidades vigentes, extrae TODAS
    5. Si no encuentras información específica para algún campo, déjalo vacío o usa una lista vacía
    
    {format_instructions}
    """
    
    parser = JsonOutputParser(pydantic_object=FundingOpportunityList)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Título: {title}\n\nContenido: {content}\n\nURL: {url}"),
    ])
    
    chain = prompt_template | llm | parser
    
    all_opportunities = []
    
    for result in relevant_results:
        try:
            print(f"   -> Extrayendo de: {result.get('url', '')[:60]}")
            
            extraction = chain.invoke({
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "current_date": current_date,
                "format_instructions": parser.get_format_instructions()
            })
            
            opportunities = extraction.get("opportunities", [])
            
            for opp in opportunities:
                all_opportunities.append({
                    "origin": opp.get("origin", ""),
                    "description": opp.get("description", ""),
                    "financing_type": opp.get("financing_type", ""),
                    "main_requirements": opp.get("main_requirements", []),
                    "application_deadline": opp.get("application_deadline", ""),
                    "opportunity_url": opp.get("opportunity_url", result.get("url", ""))
                })
            
            print(f"      ✅ Encontradas {len(opportunities)} oportunidades")
            time.sleep(2)  # Pausa entre extracciones
            
        except Exception as e:
            print(f"   ⚠️ Error en extracción: {e}")
            continue
    
    print(f"   ✅ Total de oportunidades extraídas: {len(all_opportunities)}")
    return all_opportunities


# ============================================================================
# NODO PRINCIPAL
# ============================================================================

def research_opportunities(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo de investigación de oportunidades.
    Ejecuta el flujo completo de descubrimiento de oportunidades de inversión.
    """
    print("\n" + "="*80)
    print("NODO: INVESTIGACIÓN DE OPORTUNIDADES")
    print("="*80)
    
    # Obtenemos la información del proyecto
    project_title = state.get("project_title", "")
    project_description = state.get("project_description", "")
    
    project_details = f"""
    Título del Proyecto: {project_title}
    
    Descripción del Proyecto:
    {project_description}
    """
    
    print(f"\nProyecto: {project_title}")
    
    try:
        # Obtenemos el LLM configurado
        llm = get_llm()
        
        # PASO 1: Generar queries de búsqueda
        queries = generate_search_queries(project_details, llm)
        
        if not queries:
            return {
                "investment_opportunities": [],
                "messages": [{
                    "role": "assistant",
                    "content": "No se pudieron generar queries de búsqueda."
                }]
            }
        
        # PASO 2: Buscar en la web
        search_results = search_web(queries)
        
        if not search_results:
            return {
                "investment_opportunities": [],
                "messages": [{
                    "role": "assistant",
                    "content": "No se encontraron resultados en la búsqueda web."
                }]
            }
        
        # PASO 3: Escrutinar resultados (filtrar relevantes)
        relevant_results = scrutinize_results(search_results, llm)
        
        if not relevant_results:
            return {
                "investment_opportunities": [],
                "messages": [{
                    "role": "assistant",
                    "content": f"Se analizaron {len(search_results)} resultados pero ninguno fue relevante."
                }]
            }
        
        # PASO 4: Extraer oportunidades
        opportunities = extract_opportunities(relevant_results, llm)
        
        # Mensaje de confirmación
        confirmation_message = {
            "role": "assistant",
            "content": f"✅ Investigación completada para '{project_title}'.\n"
                       f"Se encontraron {len(opportunities)} oportunidades de inversión relevantes."
        }
        
        print("\n" + "="*80)
        print(f"INVESTIGACIÓN COMPLETADA: {len(opportunities)} oportunidades encontradas")
        print("="*80 + "\n")
        
        return {
            "investment_opportunities": opportunities,
            "messages": [confirmation_message]
        }
        
    except Exception as e:
        print(f"\n❌ Error durante la investigación: {e}")
        import traceback
        traceback.print_exc()
        
        error_message = {
            "role": "assistant",
            "content": f"Ocurrió un error durante la investigación: {str(e)}"
        }
        
        return {
            "investment_opportunities": [],
            "messages": [error_message]
        }
