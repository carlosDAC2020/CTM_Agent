# Guía de Integración - Flujo de Investigación de Oportunidades

## 📋 Resumen

Se ha integrado exitosamente el flujo de investigación de oportunidades en el agente CTM. El agente ahora ejecuta automáticamente una búsqueda inteligente de oportunidades de inversión cuando se ingresa información de un proyecto.

## 🏗️ Arquitectura del Flujo

```
Usuario ingresa información del proyecto
         ↓
   [ingest_info]
   - Valida y confirma recepción
   - Prepara el estado
         ↓
[research_opportunities]
   ├─ Paso 1: Generación de Queries
   │  └─ Genera 5 ideas × 2 queries (internacional/nacional)
   ├─ Paso 2: Búsqueda Web
   │  └─ Busca en Tavily API + Brave Search (2 resultados por query cada uno)
   ├─ Paso 3: Escrutinio
   │  └─ Filtra solo fuentes relevantes (convocatorias reales)
   └─ Paso 4: Extracción
      ├─ Extrae información estructurada de oportunidades
      └─ Filtra oportunidades vigentes (deadline > fecha actual)
         ↓
[select_opportunities] ⏸️ INTERRUPCIÓN AQUÍ
   - Presenta las oportunidades al usuario
   - Usa interrupt() para pausar la ejecución
   - Espera selección del usuario (lista de índices o "all")
   - Usuario reanuda con Command(resume=...)
         ↓
[academic_research]
   - Busca papers académicos para las oportunidades seleccionadas
         ↓
[generate_report]
   - Genera reporte de mejoras basado en la investigación
         ↓
[chat_responder]
   - Finaliza el flujo
         ↓
      [__end__]
```

## 📁 Estructura de Archivos

```
src/agent/
├── graph.py                    # Grafo principal del agente (ACTUALIZADO)
├── state.py                    # Estado compartido (ProjectState)
├── config.py                   # Configuración LLM estándar
└── nodes/
    ├── ingestion.py           # Nodo de ingestión
    ├── research.py            # Nodo de investigación de oportunidades
    ├── chat.py                # Nodo de selección (NUEVO) y chat responder
    └── analysis.py            # Nodos de investigación académica y reporte
```

## 🔧 Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# API Key para el modelo de lenguaje (Gemini)
GOOGLE_API_KEY=tu_api_key_de_google

# API Keys para búsqueda web (al menos una es requerida)
TAVILY_API_KEY=tu_api_key_de_tavily
BRAVE_SEARCH_API_KEY=tu_api_key_de_brave  # Opcional, pero recomendado
```

### 2. Dependencias

Instala las dependencias necesarias:

```bash
pip install langgraph langchain langchain-google-genai python-dotenv tavily-python pydantic
```

## 🚀 Uso del Agente

### Ejemplo Básico

```python
from src.agent.graph import graph

# Preparar el estado inicial
initial_state = {
    "project_title": "Mi Proyecto Innovador",
    "project_description": "Descripción detallada del proyecto...",
    "document_paths": [],
    "investment_opportunities": [],
    "selected_opportunities": [],
    "academic_papers": [],
    "improvement_report": "",
    "messages": []
}

# Ejecutar el agente
final_state = graph.invoke(initial_state)

# Obtener las oportunidades encontradas
opportunities = final_state["investment_opportunities"]
```

### Ejecutar el Ejemplo Completo

```bash
python example_usage.py
```

## 📊 Estructura de Datos

### Input (ProjectState)

```python
{
    "project_title": str,              # Título del proyecto
    "project_description": str,        # Descripción detallada
    "document_paths": List[str],       # Rutas a documentos (opcional)
    "investment_opportunities": [],    # Se llenará automáticamente
    "selected_opportunities": [],      # Para futuros pasos
    "academic_papers": [],             # Para futuros pasos
    "improvement_report": "",          # Para futuros pasos
    "messages": []                     # Historial de conversación
}
```

### Output (Oportunidades)

```python
{
    "origin": str,                     # Organización que ofrece la financiación
    "description": str,                # Resumen de la oportunidad
    "financing_type": str,             # Tipo (grant, inversión, subsidio)
    "main_requirements": List[str],    # Requisitos principales
    "application_deadline": str,       # Fecha límite (YYYY-MM-DD)
    "opportunity_url": str             # URL de la convocatoria
}
```

## 🎯 Características Clave

### ✅ Independiente
- **No depende de los flows originales**: Todo el flujo está contenido en `research.py`
- **Sin dependencias de base de datos**: No requiere Django ni modelos de DB
- **Configuración estándar**: Usa `get_llm()` del `config.py` existente

### ✅ Inteligente
- **Generación estratégica de queries**: 5 ideas × 2 versiones (internacional/nacional)
- **Filtrado inteligente**: Descarta noticias, blogs y directorios
- **Extracción estructurada**: Identifica requisitos, fechas y URLs específicas
- **Filtrado temporal**: Solo retorna oportunidades vigentes (deadline posterior a la fecha actual)

### ✅ Robusto
- **Manejo de errores**: Captura y reporta errores en cada paso
- **Rate limiting**: Respeta límites de API (4.1s entre escrutinios)
- **Logging detallado**: Muestra progreso en cada paso

## 🔍 Flujo Detallado

### Paso 1: Generación de Queries
- Analiza el título y descripción del proyecto
- Genera 5 ideas de búsqueda diferentes
- Crea 2 versiones por idea (inglés/español)
- **Output**: 10 queries estratégicas

### Paso 2: Búsqueda Web
- Ejecuta cada query en Tavily API (si está configurado)
- Ejecuta cada query en Brave Search (si está configurado)
- Obtiene 2 resultados por query de cada motor
- **Output**: ~20-40 resultados de búsqueda (dependiendo de los motores habilitados)

### Paso 3: Escrutinio
- Analiza cada resultado con LLM
- Filtra solo convocatorias reales
- Descarta noticias, blogs, directorios
- **Output**: 3-5 fuentes relevantes (típicamente)

### Paso 4: Extracción
- Analiza el contenido de cada fuente
- Extrae información estructurada
- Identifica múltiples oportunidades por fuente
- **Filtra oportunidades vencidas**: Solo incluye deadlines posteriores a la fecha actual
- **Validación de fechas**: Verifica formato YYYY-MM-DD y compara con fecha actual
- **Output**: Lista de oportunidades vigentes con detalles completos

## ⚙️ Personalización

### Ajustar Número de Resultados

En `research.py`, línea 137:
```python
response = client.search(query=query, max_results=2)  # Cambiar aquí
```

### Ajustar Rate Limiting

En `research.py`, línea 215:
```python
time.sleep(4.1)  # Ajustar tiempo de espera
```

### Modificar Prompts

Los prompts están en las funciones:
- `generate_search_queries()` - línea 64
- `scrutinize_results()` - línea 170
- `extract_opportunities()` - línea 238

## 🐛 Troubleshooting

### Error: "Ni TAVILY_API_KEY ni BRAVE_SEARCH_API_KEY configuradas"
**Solución**: Agrega al menos una de las API keys a tu archivo `.env`:
- `TAVILY_API_KEY` (recomendado)
- `BRAVE_SEARCH_API_KEY` (opcional, pero mejora resultados)

### Error: "GOOGLE_API_KEY no está configurada"
**Solución**: Agrega `GOOGLE_API_KEY` a tu archivo `.env`

### No se encuentran oportunidades
**Posibles causas**:
- Descripción del proyecto muy genérica
- Queries no generan resultados relevantes
- Filtro de escrutinio muy estricto

**Solución**: Proporciona una descripción más detallada del proyecto con palabras clave específicas.

## 📈 Próximos Pasos

El flujo actual cubre la fase de **Discovery** (descubrimiento). Los siguientes pasos podrían incluir:

1. **Selección de Oportunidades**: Filtrar las más relevantes para el proyecto
2. **Enriquecimiento**: Obtener información adicional de cada oportunidad
3. **Generación de Reportes**: Crear documentos de análisis
4. **Búsqueda de Papers**: Encontrar investigación académica relacionada

## 📝 Notas Importantes

- El flujo es **completamente independiente** de los flows originales
- Usa la **configuración estándar** del agente (`get_llm()`)
- **No requiere base de datos** ni Django
- Es **fácil de mantener** y modificar
- Está **listo para producción**

---

**Autor**: Cascade AI  
**Fecha**: Octubre 2025  
**Versión**: 1.0
