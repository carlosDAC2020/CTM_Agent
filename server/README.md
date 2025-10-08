# Agent Architecture

Este directorio contiene la implementación del agente multi-nodo usando LangGraph.

## Estructura del Proyecto

```
agent/
├── __init__.py           # Exportaciones principales
├── graph.py              # Definición del grafo principal (LIMPIO)
├── state.py              # Estado y contexto del agente
├── config.py             # Configuración y constantes
├── routing.py            # Funciones de enrutamiento
├── nodes/                # Nodos del grafo
│   ├── __init__.py
│   ├── router_node.py    # Nodo que dirige el flujo
│   ├── llm_node.py       # Nodo LLM simple
│   ├── math_node.py      # Nodo de operaciones matemáticas
│   └── complex_chain_node.py  # Nodo de flujos complejos
└── utils/                # Utilidades
    ├── __init__.py
    └── math_utils.py     # Utilidades matemáticas
```

## Flujo del Agente

```
Usuario → Router → [Math | Complex Chain | LLM] → Respuesta
```

### Nodos Disponibles

1. **Router Node**: Analiza la entrada y decide qué nodo ejecutar
2. **Math Operations**: Evalúa expresiones matemáticas de forma segura
3. **Complex Chain**: Ejecuta flujos multi-paso (análisis, sub-preguntas, síntesis)
4. **Call Model**: Respuestas generales usando el LLM

## Cómo Agregar un Nuevo Nodo

1. Crear archivo en `nodes/nuevo_nodo.py`
2. Implementar función async que reciba `State` y `Runtime[Context]`
3. Importar en `nodes/__init__.py`
4. Agregar al grafo en `graph.py`
5. Actualizar lógica de routing si es necesario

## Ejemplo de Uso

```python
from agent.graph import graph
from agent.state import State
from langchain_core.messages import HumanMessage

# Crear estado inicial
state = State(messages=[HumanMessage(content="Calcula 25 * 4")])

# Ejecutar grafo
result = await graph.ainvoke(state)
```


langgraph dev --allow-blocking