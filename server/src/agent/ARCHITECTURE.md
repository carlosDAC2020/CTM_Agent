# Arquitectura del Agente Multi-Nodo

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                         USUARIO                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   __start__ │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   ROUTER    │ ◄─── Analiza tipo de consulta
                  └──────┬──────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ MATH_OPERATIONS│ │  CALL_MODEL  │ │ COMPLEX_CHAIN    │
│                │ │              │ │                  │
│ • Eval seguro  │ │ • LLM simple │ │ • Multi-paso     │
│ • AST parsing  │ │ • Gemini     │ │ • Análisis       │
│ • Operadores   │ │              │ │ • Síntesis       │
└────────┬───────┘ └──────┬───────┘ └────────┬─────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   __end__   │
                  └─────────────┘
```

## Estructura de Archivos

```
agent/
│
├── 📄 graph.py                    # ⭐ ARCHIVO PRINCIPAL (55 líneas)
│   └── Construye el grafo y conecta todos los nodos
│
├── 📄 state.py                    # Estado compartido
│   ├── State (messages, next_node, results)
│   └── Context (configuración)
│
├── 📄 config.py                   # Configuración centralizada
│   ├── get_llm() → Instancia del modelo
│   ├── MATH_KEYWORDS
│   └── COMPLEX_KEYWORDS
│
├── 📄 routing.py                  # Lógica de enrutamiento
│   └── route_after_router()
│
├── 📁 nodes/                      # Nodos del grafo
│   ├── router_node.py            # Decide el flujo
│   ├── llm_node.py               # LLM simple
│   ├── math_node.py              # Operaciones matemáticas
│   └── complex_chain_node.py     # Flujos complejos
│
└── 📁 utils/                      # Utilidades reutilizables
    └── math_utils.py             # Evaluación matemática segura
```

## Ventajas de esta Arquitectura

### ✅ Separación de Responsabilidades
- Cada nodo en su propio archivo
- Utilidades separadas de la lógica de negocio
- Configuración centralizada

### ✅ Mantenibilidad
- `graph.py` ahora tiene solo **55 líneas** (antes 223)
- Fácil encontrar y modificar cada componente
- Código autodocumentado

### ✅ Escalabilidad
- Agregar nuevos nodos es trivial
- No afecta código existente
- Testing independiente por módulo

### ✅ Reutilización
- Utilidades pueden usarse fuera del grafo
- Nodos pueden combinarse de diferentes formas
- Configuración compartida

## Cómo Agregar un Nuevo Nodo

### Paso 1: Crear el archivo del nodo
```python
# nodes/mi_nuevo_nodo.py
from typing import Any, Dict
from langgraph.runtime import Runtime
from ..state import State, Context

async def mi_nuevo_nodo(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Descripción del nodo."""
    # Tu lógica aquí
    return {"messages": [...], "next_node": None}
```

### Paso 2: Exportar en `nodes/__init__.py`
```python
from .mi_nuevo_nodo import mi_nuevo_nodo
__all__ = [..., 'mi_nuevo_nodo']
```

### Paso 3: Agregar al grafo en `graph.py`
```python
builder.add_node("mi_nuevo_nodo", mi_nuevo_nodo)
builder.add_edge("mi_nuevo_nodo", "__end__")
```

### Paso 4: Actualizar router (opcional)
```python
# nodes/router_node.py
if "mi_condicion" in user_input:
    return {"next_node": "mi_nuevo_nodo"}
```

## Patrones de Diseño Implementados

### 🎯 Strategy Pattern
Cada nodo es una estrategia diferente para procesar la entrada

### 🔀 Router Pattern
El router decide dinámicamente qué estrategia usar

### 🏭 Factory Pattern
`build_graph()` construye el grafo completo

### 📦 Module Pattern
Cada módulo encapsula funcionalidad relacionada

## Testing

Cada módulo puede testearse independientemente:

```python
# Test del nodo matemático
from agent.nodes.math_node import math_operations
from agent.state import State

state = State(messages=[HumanMessage(content="2 + 2")])
result = await math_operations(state, runtime)
assert result["math_result"] == "4"
```

## Métricas de Mejora

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas en graph.py | 223 | 55 | ⬇️ 75% |
| Archivos | 1 | 11 | ⬆️ Modular |
| Responsabilidades | Todas | 1 por archivo | ✅ |
| Testabilidad | Baja | Alta | ⬆️⬆️ |
| Mantenibilidad | Baja | Alta | ⬆️⬆️ |
