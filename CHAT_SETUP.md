# 💬 Chat Interface con Visualización Completa del Flujo

Esta implementación te permite ver **cada paso** que realiza tu agente multi-nodo en tiempo real, incluyendo:

- ✅ **Flujo de nodos**: Router → Math/Complex/LLM → End
- ✅ **Llamadas a herramientas**: LLM, evaluaciones matemáticas, etc.
- ✅ **Pasos intermedios**: Análisis, síntesis, decisiones
- ✅ **Eventos en tiempo real**: Streaming con Server-Sent Events
- ✅ **Interfaz visual**: Chat + Panel de flujo lado a lado

## 🚀 Inicio Rápido

### Opción 1: Script Automático
```bash
cd C:\Users\LABSISTEMAS03\Documents\carlos\CTM_Agent
python start_chat_server.py
```

### Opción 2: Manual
```bash
# 1. Iniciar servidor
cd C:\Users\LABSISTEMAS03\Documents\carlos\CTM_Agent\server\src
python streaming_server.py

# 2. Abrir chat_interface.html en tu navegador
```

## 🎯 Cómo Usar

### **Prueba Operaciones Matemáticas**
```
Usuario: "Calcula 25 * 4 + 10"
```
**Verás en el flujo:**
- 🔵 Router: Detecta operación matemática
- 🟡 Math Node: Extrae expresión "25 * 4 + 10"
- 🟢 Tool Call: safe_eval_math()
- 🟢 Tool Result: 110
- 💬 Respuesta: "El resultado de 25 * 4 + 10 es: 110"

### **Prueba Flujos Complejos**
```
Usuario: "Analiza las ventajas de Python vs JavaScript"
```
**Verás en el flujo:**
- 🔵 Router: Detecta consulta compleja
- 🟡 Complex Chain: Paso 1 - Análisis
- 🟢 Tool Call: llm_analysis
- 🟡 Complex Chain: Paso 2 - Q&A
- 🟢 Tool Call: llm_qa
- 🟡 Complex Chain: Paso 3 - Síntesis
- 🟢 Tool Call: llm_synthesis
- 💬 Respuesta final sintetizada

### **Prueba Consultas Generales**
```
Usuario: "¿Qué es LangGraph?"
```
**Verás en el flujo:**
- 🔵 Router: Detecta consulta general
- 🟡 LLM Node: Llamada directa a Gemini
- 🟢 Tool Call: gemini_llm
- 💬 Respuesta del modelo

## 🎨 Interfaz Visual

### **Panel Izquierdo: Chat**
- Conversación normal con el agente
- Mensajes del usuario y respuestas
- Indicadores de estado (enviando, procesando)

### **Panel Derecho: Flujo del Agente**
- **🔵 Node Start/End**: Inicio y fin de nodos
- **🟡 Steps**: Pasos intermedios del procesamiento
- **🟢 Tool Calls/Results**: Llamadas y resultados de herramientas
- **💬 Messages**: Mensajes generados
- **🔴 Errors**: Errores si ocurren

## 📊 Tipos de Eventos

| Tipo | Color | Descripción |
|------|-------|-------------|
| `node_start` | 🔵 Azul | Inicio de un nodo |
| `node_end` | 🟢 Verde | Fin de un nodo |
| `step` | 🟡 Naranja | Paso intermedio |
| `tool_call` | 🟣 Púrpura | Llamada a herramienta |
| `tool_result` | 🟢 Verde Agua | Resultado de herramienta |
| `message` | 🔵 Índigo | Mensaje generado |
| `error` | 🔴 Rojo | Error ocurrido |

## 🔧 Arquitectura Técnica

### **Backend (FastAPI + Streaming)**
```
streaming_server.py
├── /chat/stream (POST) → Server-Sent Events
├── /health (GET) → Status check
└── / (GET) → API info
```

### **Frontend (HTML + JavaScript)**
```
chat_interface.html
├── Chat Panel → Conversación
├── Flow Panel → Visualización de eventos
└── EventSource → Streaming en tiempo real
```

### **Agent Events System**
```
events.py
├── AgentEvent → Estructura de eventos
├── EventEmitter → Sistema de emisión
└── Event Types → node_start, step, tool_call, etc.
```

## 🛠️ Personalización

### **Agregar Nuevos Tipos de Eventos**
```python
# En events.py
@staticmethod
def custom_event(node_name: str, data: Any) -> "AgentEvent":
    return AgentEvent(
        type="custom",
        node=node_name,
        timestamp=datetime.now().isoformat(),
        data=data
    )
```

### **Modificar Estilos de la Interfaz**
```css
/* En chat_interface.html */
.flow-event.custom {
    background: #your-color;
    border-color: #your-border;
}
```

### **Agregar Nuevos Nodos con Tracking**
```python
# En tu nuevo nodo
events = list(state.events)
events.append(asdict(AgentEvent.node_start("mi_nodo", "Descripción")))
# ... tu lógica ...
events.append(asdict(AgentEvent.node_end("mi_nodo", "Completado")))
return {"events": events, ...}
```

## 🐛 Troubleshooting

### **Error de CORS**
- Asegúrate de que el servidor esté corriendo en puerto 8000
- Verifica que CORS esté habilitado en `streaming_server.py`

### **No se ven eventos**
- Revisa que los nodos estén retornando `events` en el estado
- Verifica la consola del navegador para errores de JavaScript

### **Servidor no inicia**
- Verifica que todas las dependencias estén instaladas
- Asegúrate de estar en el directorio correcto
- Revisa que el puerto 8000 esté libre

## 📈 Próximas Mejoras

- [ ] Persistencia de conversaciones
- [ ] Exportar flujos como diagramas
- [ ] Métricas de rendimiento
- [ ] Filtros de eventos
- [ ] Modo debug avanzado
- [ ] Integración con LangSmith

¡Disfruta explorando cada paso de tu agente! 🎉
