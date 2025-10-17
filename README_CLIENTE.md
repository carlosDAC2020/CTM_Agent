# 🚀 Mini-Cliente Agente CTM - Análisis de Inversiones

Cliente completo para gestionar el ciclo de vida del Agente CTM de análisis de inversiones con base de datos de proyectos y persistencia de resultados.

## 📋 Características

- ✅ **Base de datos de proyectos**: 8 proyectos de prueba pre-configurados
- ✅ **Persistencia de threads**: Guarda historial de ejecuciones
- ✅ **Gestión completa del agente**: Manejo automático de interrupciones
- ✅ **Modo interactivo**: Selección de oportunidades y chat con el agente
- ✅ **Historial de ejecuciones**: Consulta threads anteriores
- ✅ **Proyectos personalizados**: Crea tus propios proyectos

## 🗂️ Archivos

```
CTM_Agent/
├── test_agent.py              # Mini-cliente principal
├── projects_database.json     # Base de datos de proyectos
├── threads_history.json       # Historial de threads ejecutados
└── README_CLIENTE.md          # Esta documentación
```

## 🚀 Uso

### 1. Iniciar el servidor LangGraph

```bash
# En el directorio ctm-investment-agent
langgraph dev
```

El servidor debe estar corriendo en `http://127.0.0.1:2024`

### 2. Ejecutar el cliente

```bash
python test_agent.py
```

### 3. Flujo de uso

1. **Seleccionar proyecto**: Elige de la base de datos o crea uno personalizado
2. **Análisis automático**: El agente busca oportunidades de financiación
3. **Selección de oportunidades**: Elige cuáles analizar en detalle
4. **Investigación académica**: El agente busca papers relevantes
5. **Reporte de mejoras**: Genera recomendaciones
6. **Modo chat**: Haz preguntas sobre el proyecto y resultados

## 📊 Base de Datos de Proyectos

La base de datos incluye 8 proyectos en diferentes categorías:

1. **Energía Renovable**: Sistema de energía solar para comunidades rurales
2. **Salud Digital**: Plataforma de telemedicina con IA
3. **AgriTech**: Agricultura de precisión con IoT y drones
4. **Blockchain**: Trazabilidad en cadena de suministro de café
5. **EdTech**: App de educación adaptativa con realidad aumentada
6. **Smart Cities**: Gestión de residuos inteligente
7. **FinTech**: Microcréditos con scoring alternativo
8. **Movilidad Eléctrica**: Red de estaciones de carga rápida

## 🎮 Menú Principal

```
📁 BASE DE DATOS DE PROYECTOS
======================================================================

[0] Sistema de Energía Solar para Comunidades Rurales
    📂 Categoría: Energía Renovable
    💰 Presupuesto: $250,000
    ⏱️  Duración: 18 meses
    🏷️  Tags: energía solar, sostenibilidad, comunidades rurales...

[1] Plataforma de Telemedicina con IA para Diagnóstico Temprano
    ...

======================================================================
[C] Crear proyecto personalizado
[H] Ver historial de threads
[Q] Salir
======================================================================
```

## 📝 Historial de Threads

Cada ejecución se guarda con la siguiente información:

```json
{
  "thread_id": "uuid-del-thread",
  "assistant_id": "uuid-del-assistant",
  "project_id": "proj_001",
  "project_title": "Nombre del proyecto",
  "created_at": "2025-10-16T14:30:00",
  "duration_seconds": 245,
  "opportunities_found": 15,
  "opportunities_selected": 3,
  "papers_found": 8,
  "report_generated": true,
  "total_interactions": 5,
  "status": "completed"
}
```

## 🔄 Flujo de Ejecución

```
┌─────────────────────────────────────┐
│  1. Seleccionar/Crear Proyecto     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  2. Crear Assistant y Thread        │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  3. Ingesta de Información          │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  4. Búsqueda de Oportunidades       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  5. INTERRUPCIÓN: Selección         │
│     Usuario elige oportunidades     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  6. Investigación Académica         │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  7. Generación de Reporte           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  8. INTERRUPCIÓN: Modo Chat         │
│     Usuario hace preguntas          │
│     (Bucle hasta 'end')             │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  9. Guardar en Historial            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  10. Mostrar Resultados Finales     │
└─────────────────────────────────────┘
```

## 💬 Comandos en Modo Chat

Durante el modo chat interactivo, puedes:

- Hacer preguntas sobre el proyecto
- Consultar sobre oportunidades específicas
- Pedir detalles del reporte
- Solicitar recomendaciones de implementación
- Escribir `end`, `fin`, `finalizar`, `salir` o `exit` para terminar

## 🛠️ Personalización

### Agregar nuevos proyectos

Edita `projects_database.json`:

```json
{
  "projects": [
    {
      "id": "proj_009",
      "title": "Tu Proyecto",
      "description": "Descripción detallada...",
      "category": "Categoría",
      "budget": 100000,
      "duration_months": 12,
      "tags": ["tag1", "tag2", "tag3"]
    }
  ]
}
```

### Configurar URL del servidor

Edita en `test_agent.py`:

```python
LANGGRAPH_API_URL = "http://127.0.0.1:2024"  # Cambia el puerto si es necesario
```

## 📊 Ejemplo de Salida

```
🚀 MINI-CLIENTE AGENTE CTM - ANÁLISIS DE INVERSIONES
======================================================================

📊 Funcionalidades:
  • Base de datos de proyectos de prueba
  • Persistencia de threads y resultados
  • Gestión completa del ciclo de vida del agente
  • Historial de ejecuciones

======================================================================

✅ Asistente encontrado. ID: 123e4567-e89b-12d3-a456-426614174000

📁 BASE DE DATOS DE PROYECTOS
...

👉 Selecciona una opción: 0

✅ PROYECTO SELECCIONADO: Sistema de Energía Solar para Comunidades Rurales
──────────────────────────────────────────────────────────────────────

📋 Proyecto de implementación de paneles solares fotovoltaicos...

──────────────────────────────────────────────────────────────────────

Presiona Enter para iniciar el análisis...

✅ Hilo creado exitosamente. ID: 987f6543-e21c-34d5-b678-543216789abc

🔄 MONITOREANDO EJECUCIÓN DEL AGENTE...
──────────────────────────────────────────────────────────────────────
   📍 Estado: busy | Siguiente: research_opportunities

⏸️  AGENTE PAUSADO - Esperando input del usuario
──────────────────────────────────────────────────────────────────────

⚠️  INTERRUPCIÓN: SELECCIÓN DE OPORTUNIDADES
======================================================================

🔍 Se encontraron 15 oportunidades de financiación:

  [0] Horizonte Europa - Energía Limpia
      📋 Financiación para proyectos de energía renovable en zonas rurales...
      💰 Tipo: Grant | 📅 Deadline: 2025-12-31

...

👉 Tu selección: 0,1,2

✅ Seleccionaste 3 oportunidades: [0, 1, 2]

...

💬 MODO CHAT INTERACTIVO ACTIVADO
======================================================================

El reporte de mejoras y la propuesta conceptual están listos.

📚 Puedes hacer preguntas sobre:
   • El proyecto y sus componentes
   • Las oportunidades de financiación identificadas
   • Las recomendaciones del reporte
   ...

💭 Tu pregunta: ¿Cuál es la mejor oportunidad para mi proyecto?

[Respuesta del agente...]

💭 Tu pregunta: end

👋 Finalizando sesión de chat...

🎉 RESULTADOS FINALES DEL AGENTE CTM
======================================================================

📌 Proyecto: Sistema de Energía Solar para Comunidades Rurales

💼 Oportunidades encontradas: 15
✅ Oportunidades seleccionadas: 3
📚 Papers académicos consultados: 8

📄 Reporte de mejoras generado (2543 caracteres)

💬 Total de interacciones: 4

======================================================================

💾 Thread guardado en historial

✅ SESIÓN FINALIZADA
======================================================================

📊 Thread ID: 987f6543-e21c-34d5-b678-543216789abc
🤖 Assistant ID: 123e4567-e89b-12d3-a456-426614174000
⏱️  Duración total: 245 segundos (4.1 minutos)

💡 Puedes consultar el estado completo en:
   http://127.0.0.1:2024/threads/987f6543-e21c-34d5-b678-543216789abc/state

💾 Thread guardado en: threads_history.json

======================================================================
```

## 🐛 Troubleshooting

### Error: "Connection refused"

- Verifica que el servidor LangGraph esté corriendo
- Comprueba que el puerto sea el correcto (2024 por defecto)

### Error: "No se encontró projects_database.json"

- Asegúrate de ejecutar el script desde el directorio raíz del proyecto
- Verifica que el archivo exista en el mismo directorio que `test_agent.py`

### El agente no responde

- Revisa los logs del servidor LangGraph
- Verifica que el grafo del agente esté correctamente compilado

## 📚 Recursos

- **Documentación LangGraph**: https://langchain-ai.github.io/langgraph/
- **API CTM**: Ver `api_ctm_agent/README.md`
- **Agente CTM**: Ver `ctm-investment-agent/README.md`

---

**Desarrollado para CTM Investment Analysis** 🚀
