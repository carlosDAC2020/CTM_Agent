# src/agent/nodes/research.py

import os
import time
from typing import Dict, Any, List
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from tavily import TavilyClient
from typing import Literal 

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
    relevance_category: Literal["Direct Funding Opportunity", "Funding Source Portal", "Potential Funding Organization", "Not Relevant"] = Field(
        description="Categorization of the search result's relevance."
    )
    justification: str = Field(description="A brief explanation for the chosen category.")

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
    You are a strategic research analyst specializing in securing funding for technology and innovation projects.
    Your task is to generate highly effective search queries to find funding opportunities (grants, venture capital, government calls for proposals) based on a project description.

    Analyze the project's core technologies, target sector, and potential impact. Create 5 distinct search concepts.
    For each concept, generate two query variations:
    1.  **International (English):** Combine technical terms with financial keywords like "funding", "grants", "seed round", "R&D funding". Use boolean operators like OR and AND. Be specific.
        Example for a drone project: `("precision agriculture" AND "drone technology") OR "agritech innovation fund"`
    2.  **National (Colombia - Spanish):** Translate the concept into Spanish, using local terms like "convocatorias", "financiación", "capital semilla", "proyectos I+D+i". Target it specifically to Colombia.

    RULES:
    - Focus on finding direct funding opportunities, not just news articles.
    - Be creative and combine different keywords in each query.
    - Avoid overly broad terms.

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
    Filters and categorizes search results to identify relevant funding sources.
    """
    print(f"\n[3/4] Escrutando {len(search_results)} resultados...")
    
    # --- PROMPT DE ESCRUTINIO REINVENTADO ---
    system_prompt = """
    You are an expert financial analyst. Your task is to categorize a web search result to determine its potential for finding project funding.
    Think step-by-step. First, analyze the content. Then, assign one of the four categories below.

    Here are the categories:
    1.  **"Direct Funding Opportunity"**: This is the best category. The page is a specific, active call for proposals, a grant announcement, or a direct application page. It has a clear objective, eligibility criteria, and often a deadline.
    2.  **"Funding Source Portal"**: The page is a list or portal of multiple funding opportunities. For example, a government page listing all their active grants, or a foundation's "open calls" section.
    3.  **"Potential Funding Organization"**: The page is the homepage or a high-level page of an organization that is known to fund projects in this area (e.g., a government ministry of science, a venture capital firm, a corporate foundation). It doesn't list a specific call, but it's a very strong lead.
    4.  **"Not Relevant"**: The page is a news article, a blog post, a scientific paper, a finished project, or a general information page that does not directly relate to obtaining funding.

    Your goal is to find actionable leads. Err on the side of inclusion for categories 2 and 3.

    {format_instructions}
    """
    
    parser = JsonOutputParser(pydantic_object=ScrutinyResult)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Analyze the following web page content:\n\nTitle: {title}\nURL: {url}\n\nContent Snippet:\n{content}"),
    ])
    
    chain = prompt_template | llm | parser
    
    relevant_results = []
    
    for result in search_results:
        try:
            # Limitar el contenido para no exceder el contexto del LLM
            content_snippet = result.get("content", "")
            if len(content_snippet) > 1500:
                content_snippet = content_snippet[:1500]

            scrutiny = chain.invoke({
                "title": result.get("title", ""),
                "content": content_snippet,
                "url": result.get("url", ""),
                "format_instructions": parser.get_format_instructions()
            })
            
            category = scrutiny.get("relevance_category")
            
            # --- LÓGICA DE FILTRADO MEJORADA ---
            # Aceptamos las 3 primeras categorías
            if category and category != "Not Relevant":
                print(f"   ✅ Relevante ({category}): {result.get('title', '')[:60]}")
                relevant_results.append(result)
            else:
                print(f"   ❌ Descartado: {result.get('title', '')[:60]}")
            
            time.sleep(10) 
            
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
# NODOS MODULARES
# ============================================================================

# NODO 1: Genera las queries de búsqueda
def generate_queries_node(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo que genera las queries de búsqueda y las guarda en el estado.
    """
    print("\n" + "="*80)
    print("NODO: Generando Queries de Búsqueda")
    print("="*80)
    
    llm = get_llm()
    project_details = f"Título: {state['project_title']}\nDescripción: {state['project_description']}"

    existing_opportunities = state.get("investment_opportunities", [])
    if existing_opportunities:
        print("   -> Detectadas oportunidades existentes. Buscando alternativas.")
        
        # Formateamos las oportunidades existentes para el prompt
        opportunities_summary = "\n".join([
            f"- {opp.get('origin', 'N/A')}: {opp.get('description', 'N/A')[:100]}..."
            for opp in existing_opportunities
        ])
        
        # Añadimos un contexto adicional al prompt para guiar al LLM
        project_details += f"""
        
        CONTEXTO ADICIONAL IMPORTANTE:
        Ya hemos encontrado las siguientes oportunidades. Por favor, genera queries para encontrar
        OPCIONES DIFERENTES Y ALTERNATIVAS a estas. No busques las mismas otra vez.
        
        Oportunidades ya encontradas:
        {opportunities_summary}
        """
    else:
        print("   -> No hay oportunidades previas. Iniciando búsqueda desde cero.")
    
    # Llama a tu función original, que ya hace el trabajo pesado
    queries = generate_search_queries(project_details, llm)
    
    # Devuelve un diccionario para actualizar el estado
    return {"search_queries": queries}

# NODO 2: Realiza la búsqueda web
def search_web_node(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo que toma las queries del estado y realiza la búsqueda web.
    """
    print("\n" + "="*80)
    print("NODO: Buscando en la Web")
    print("="*80)

    queries = state.get("search_queries", [])
    if not queries:
        return {"search_results": []}
    
    # Llama a tu función original
    results = search_web(queries)
    
    return {"search_results": results}

# NODO 3: Filtra los resultados relevantes
def scrutinize_results_node(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo que filtra los resultados de búsqueda para encontrar los más relevantes.
    """
    print("\n" + "="*80)
    print("NODO: Escrutando Resultados")
    print("="*80)

    llm = get_llm()
    results = state.get("search_results", [])
    if not results:
        return {"relevant_results": []}
    
    # Llama a tu función original
    relevant = scrutinize_results(results, llm)
    
    return {"relevant_results": relevant}

# NODO 4: Extrae las oportunidades estructuradas
def extract_opportunities_node(state: ProjectState) -> Dict[str, Any]:
    """
    Nodo final que extrae los datos y los AÑADE a la lista existente de oportunidades.
    """
    print("\n" + "="*80)
    print("NODO: Extrayendo y Acumulando Oportunidades")
    print("="*80)

    llm = get_llm()
    relevant = state.get("relevant_results", [])
    if not relevant:
        # Si no hay nuevos resultados relevantes, no hacemos nada y mantenemos las oportunidades existentes
        print("   -> No se encontraron nuevos resultados relevantes. No se añaden oportunidades.")
        return {}

    # Llama a tu función original para extraer las NUEVAS oportunidades
    new_opportunities = extract_opportunities(relevant, llm)
    
    existing_opportunities = state.get("investment_opportunities", [])
    

    # Creamos un conjunto (set) de descripciones existentes para una búsqueda rápida
    existing_descs = {opp['description'].lower() for opp in existing_opportunities}
    
    # Filtramos las nuevas oportunidades para quedarnos solo con las que no existen ya
    unique_new_opportunities = [
        opp for opp in new_opportunities if opp['description'].lower() not in existing_descs
    ]
    
    
    print(f"   -> Se extrajeron {len(new_opportunities)} nuevas oportunidades.")
    print(f"   -> Se añadirán {len(unique_new_opportunities)} oportunidades únicas al estado.")

    # Combinamos la lista existente con las nuevas oportunidades únicas
    updated_opportunities = existing_opportunities + unique_new_opportunities
    
    message = {
        "role": "assistant",
        "content": f"✅ Nueva investigación completada. Se añadieron {len(unique_new_opportunities)} oportunidades nuevas. Ahora tienes un total de {len(updated_opportunities)}."
    }
    
    return {
        "investment_opportunities": updated_opportunities,
        "messages": [message]
    }