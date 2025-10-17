# CTM Investment Agent API

API modular compatible con LangGraph para el agente de análisis de inversiones CTM.

## 🏗️ Arquitectura

La API está estructurada siguiendo las mejores prácticas de FastAPI:

```
api_ctm_agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal
│   ├── models/              # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── assistant.py
│   │   ├── thread.py
│   │   ├── run.py
│   │   ├── message.py
│   │   └── common.py
│   ├── routers/             # Endpoints organizados
│   │   ├── __init__.py
│   │   ├── assistants.py
│   │   ├── threads.py
│   │   ├── runs.py
│   │   └── system.py
│   └── services/            # Lógica de negocio
│       ├── __init__.py
│       ├── database.py
│       ├── assistant_service.py
│       ├── thread_service.py
│       ├── run_service.py
│       └── agent_service.py
├── templates/
│   └── playground.html      # Playground interactivo
├── requirements.txt
├── run.py                   # Script de inicio
└── README.md
```

## 🚀 Instalación

1. **Instalar dependencias:**

```bash
cd api_ctm_agent
pip install -r requirements.txt
```

2. **Ejecutar el servidor:**

```bash
python run.py
```

O directamente con uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Endpoints Disponibles

### **Assistants** (Instancias del Agente)

- `POST /assistants` - Crear un assistant
- `POST /assistants/search` - Buscar assistants
- `GET /assistants` - Listar todos los assistants
- `GET /assistants/{assistant_id}` - Obtener un assistant
- `PATCH /assistants/{assistant_id}` - Actualizar un assistant
- `DELETE /assistants/{assistant_id}` - Eliminar un assistant
- `POST /assistants/{assistant_id}/latest` - Establecer versión activa

### **Threads** (Conversaciones)

- `POST /threads` - Crear un thread
- `GET /threads` - Listar todos los threads
- `GET /threads/{thread_id}` - Obtener un thread
- `PATCH /threads/{thread_id}` - Actualizar un thread
- `DELETE /threads/{thread_id}` - Eliminar un thread
- `GET /threads/{thread_id}/state` - Obtener estado del thread
- `GET /threads/{thread_id}/messages` - Obtener mensajes del thread
- `POST /threads/{thread_id}/state/checkpoint` - Crear checkpoint

### **Runs** (Ejecuciones)

- `POST /threads/{thread_id}/runs` - Crear una ejecución
- `POST /threads/{thread_id}/runs/wait` - **Ejecutar y esperar resultado** ⭐
- `GET /threads/{thread_id}/runs` - Listar ejecuciones
- `GET /threads/{thread_id}/runs/{run_id}` - Obtener una ejecución
- `POST /threads/{thread_id}/runs/{run_id}/cancel` - Cancelar ejecución
- `POST /threads/{thread_id}/runs/stream` - Ejecutar con streaming

### **System** (Sistema)

- `GET /` - Información básica
- `GET /ok` - Health check
- `GET /info` - Información y estadísticas del servidor

## 🎮 Playground Interactivo

Accede al playground en: **http://localhost:8000/playground**

El playground incluye:

- ✨ Interfaz moderna estilo GitHub/LangGraph
- 🎯 Todos los endpoints disponibles
- 📝 Ejemplos pre-cargados
- 🔄 Auto-completado de IDs
- 📋 Generación de comandos cURL
- 🎨 Sintaxis highlighting para JSON

## 💡 Ejemplo de Uso

### 1. Crear un Assistant

```bash
curl -X POST "http://localhost:8000/assistants" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "agent",
    "name": "CTM Investment Agent"
  }'
```

Respuesta:
```json
{
  "assistant_id": "123e4567-e89b-12d3-a456-426614174000",
  "graph_id": "agent",
  "name": "CTM Investment Agent",
  "created_at": "2025-10-16T11:27:00",
  ...
}
```

### 2. Crear un Thread

```bash
curl -X POST "http://localhost:8000/threads" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 3. Ejecutar el Agente

```bash
curl -X POST "http://localhost:8000/threads/{thread_id}/runs/wait" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "{assistant_id}",
    "input": {
      "project_title": "Proyecto Solar",
      "project_description": "Instalación de paneles solares en zonas rurales",
      "messages": []
    }
  }'
```

## 🔧 Integración con el Agente CTM

El servicio `AgentService` en `app/services/agent_service.py` integra automáticamente el agente de inversiones CTM ubicado en `ctm-investment-agent/`.

Si el agente no está disponible, la API funciona en **modo simulado** para desarrollo.

## 📖 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🎯 Características

✅ **Arquitectura Modular** - Separación clara de responsabilidades  
✅ **Compatible con LangGraph** - Implementa el esquema completo de LangGraph  
✅ **Playground Interactivo** - Interfaz moderna para testing  
✅ **Documentación Automática** - Swagger y ReDoc integrados  
✅ **CORS Habilitado** - Listo para integraciones frontend  
✅ **Async/Await** - Operaciones asíncronas para mejor rendimiento  
✅ **Type Safety** - Validación con Pydantic  
✅ **Modo Desarrollo** - Hot reload habilitado  

## 🔄 Flujo de Trabajo Típico

1. **Crear Assistant** → Obtener `assistant_id`
2. **Crear Thread** → Obtener `thread_id`
3. **Ejecutar Run** → Enviar input y recibir output
4. **Consultar Estado** → Ver historial y estado del thread
5. **Continuar Conversación** → Enviar más runs en el mismo thread

## 🛠️ Desarrollo

Para desarrollo local con hot reload:

```bash
python run.py
```

El servidor se reiniciará automáticamente al detectar cambios en el código.

## 📝 Notas

- La base de datos actual es **en memoria** (se pierde al reiniciar)
- Para producción, implementar persistencia real (PostgreSQL, MongoDB, etc.)
- El agente CTM se carga automáticamente si está disponible
- Todos los endpoints siguen el estándar de LangGraph Platform

## 🎨 Personalización del Playground

El template del playground está en `templates/playground.html` y puede ser personalizado:

- Colores y estilos en las variables CSS (`:root`)
- Ejemplos pre-cargados en la función `loadExample()`
- Endpoints disponibles en el objeto `endpoints`

---

**Desarrollado para CTM Investment Analysis** 🚀
