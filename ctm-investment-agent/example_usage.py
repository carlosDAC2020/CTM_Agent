# example_usage.py
# Ejemplo de uso del agente CTM con flujo de investigación de oportunidades

from src.agent.graph import graph
from src.agent.state import ProjectState

def run_investment_research():
    """
    Ejemplo de cómo ejecutar el agente para investigar oportunidades de inversión.
    """
    
    # 1. Preparamos el estado inicial con la información del proyecto
    initial_state: ProjectState = {
        "project_title": "AgroTech: Plataforma de Agricultura de Precisión con Drones e IoT",
        "project_description": """
        Desarrollo de una plataforma integral de agricultura de precisión que combina 
        drones, sensores IoT y análisis de datos con IA para optimizar la producción 
        agrícola en zonas rurales de Colombia. El sistema incluye:
        
        - Drones equipados con cámaras multiespectrales para monitoreo de cultivos
        - Red de sensores IoT para medir humedad del suelo, temperatura y nutrientes
        - Plataforma de análisis con machine learning para predicción de plagas y enfermedades
        - Sistema de riego inteligente automatizado
        - App móvil para agricultores con recomendaciones en tiempo real
        - Dashboard web para análisis histórico y toma de decisiones
        
        Objetivos del proyecto:
        - Aumentar la productividad agrícola en un 30%
        - Reducir el uso de agua en un 40% mediante riego optimizado
        - Disminuir el uso de pesticidas en un 50% con detección temprana de plagas
        - Empoderar a pequeños y medianos agricultores con tecnología accesible
        - Contribuir a la seguridad alimentaria y sostenibilidad ambiental en Colombia
        
        Población objetivo: Agricultores de café, cacao, frutas y hortalizas en 
        departamentos como Antioquia, Valle del Cauca, Santander y Cundinamarca.
        """,
        "document_paths": [],
        "investment_opportunities": [],
        "selected_opportunities": [],
        "academic_papers": [],
        "improvement_report": "",
        "messages": []
    }
    
    print("="*80)
    print("AGENTE CTM - INVESTIGACIÓN DE OPORTUNIDADES DE INVERSIÓN")
    print("="*80)
    print(f"\nProyecto: {initial_state['project_title']}")
    print("\nEjecutando flujo del agente...\n")
    
    try:
        # 2. Ejecutamos el grafo con el estado inicial
        # El flujo será: ingest_info -> research_opportunities -> __end__
        final_state = graph.invoke(initial_state)
        
        print("\n" + "="*80)
        print("RESULTADOS DE LA INVESTIGACIÓN")
        print("="*80)
        
        # 3. Mostramos los resultados
        opportunities = final_state.get("investment_opportunities", [])
        
        if opportunities:
            print(f"\n✅ Se encontraron {len(opportunities)} oportunidades de inversión:\n")
            
            for idx, opp in enumerate(opportunities, 1):
                print(f"\n--- Oportunidad #{idx} ---")
                print(f"Origen: {opp.get('origin', 'N/A')}")
                print(f"Descripción: {opp.get('description', 'N/A')}")
                print(f"Tipo de Financiación: {opp.get('financing_type', 'N/A')}")
                print(f"Fecha Límite: {opp.get('application_deadline', 'N/A')}")
                print(f"URL: {opp.get('opportunity_url', 'N/A')}")
                
                requirements = opp.get('main_requirements', [])
                if requirements:
                    print("Requisitos Principales:")
                    for req in requirements:
                        print(f"  - {req}")
        else:
            print("\n⚠️ No se encontraron oportunidades de inversión.")
        
        # 4. Mostramos el historial de mensajes
        print("\n" + "="*80)
        print("HISTORIAL DE MENSAJES DEL AGENTE")
        print("="*80)
        
        messages = final_state.get("messages", [])
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            print(f"\n[{role.upper()}]: {content}")
        
        print("\n" + "="*80)
        print("EJECUCIÓN COMPLETADA")
        print("="*80)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución del agente: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    """
    Ejecuta el ejemplo de investigación de oportunidades.
    
    Requisitos previos:
    1. Configurar las variables de entorno en un archivo .env:
       - GOOGLE_API_KEY (para Gemini)
       - TAVILY_API_KEY (para búsqueda web - recomendado)
       - BRAVE_SEARCH_API_KEY (para búsqueda web adicional - opcional)
    
    2. Instalar las dependencias necesarias:
       pip install langgraph langchain langchain-google-genai langchain-community python-dotenv tavily-python pydantic
    """
    run_investment_research()
