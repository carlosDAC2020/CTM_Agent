# 📁 Estructura del Proyecto

```
api_ctm_agent/
│
├── 📄 run.py                      # Script principal para ejecutar el servidor
├── 📄 requirements.txt            # Dependencias del proyecto
├── 📄 README.md                   # Documentación principal
├── 📄 STRUCTURE.md               # Este archivo - estructura del proyecto
├── 📄 .gitignore                 # Archivos a ignorar en git
│
├── 📄 example_usage.py           # Ejemplo completo de uso de la API
├── 📄 quick_test.py              # Script de pruebas rápidas
│
├── 📂 app/                        # Aplicación principal
│   ├── 📄 __init__.py
│   ├── 📄 main.py                # Punto de entrada de FastAPI
│   │
│   ├── 📂 models/                # Modelos de datos (Pydantic)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 assistant.py       # Modelos de Assistant
│   │   ├── 📄 thread.py          # Modelos de Thread
│   │   ├── 📄 run.py             # Modelos de Run
│   │   ├── 📄 message.py         # Modelos de Message
│   │   └── 📄 common.py          # Modelos compartidos
│   │
│   ├── 📂 routers/               # Endpoints organizados por recurso
│   │   ├── 📄 __init__.py
│   │   ├── 📄 assistants.py      # Endpoints de Assistants
│   │   ├── 📄 threads.py         # Endpoints de Threads
│   │   ├── 📄 runs.py            # Endpoints de Runs
│   │   └── 📄 system.py          # Endpoints del sistema
│   │
│   └── 📂 services/              # Lógica de negocio
│       ├── 📄 __init__.py
│       ├── 📄 database.py        # Base de datos en memoria
│       ├── 📄 assistant_service.py   # Lógica de Assistants
│       ├── 📄 thread_service.py      # Lógica de Threads
│       ├── 📄 run_service.py         # Lógica de Runs
│       └── 📄 agent_service.py       # Integración con agente CTM
│
└── 📂 templates/                 # Templates HTML
    └── 📄 playground.html        # Playground interactivo
```

## 🎯 Descripción de Componentes

### **Archivos Raíz**

- **run.py**: Script para iniciar el servidor con configuración optimizada
- **requirements.txt**: Lista de dependencias necesarias
- **example_usage.py**: Ejemplo completo de cómo usar la API
- **quick_test.py**: Script para verificar que todos los endpoints funcionen

### **app/main.py**

Aplicación principal de FastAPI que:
- Configura CORS
- Registra todos los routers
- Sirve el playground
- Define eventos de inicio/cierre

### **app/models/**

Modelos Pydantic para validación de datos:

- **assistant.py**: `Assistant`, `AssistantCreate`, `AssistantUpdate`, `AssistantSearch`
- **thread.py**: `Thread`, `ThreadCreate`, `ThreadUpdate`, `ThreadState`
- **run.py**: `Run`, `RunCreate`, `RunOutput`, `RunStatus`, `StreamMode`
- **message.py**: `Message`, `MessageCreate`
- **common.py**: `Metadata`, `Config`, `ErrorResponse`

### **app/routers/**

Endpoints organizados por recurso:

- **assistants.py**: CRUD completo de assistants
- **threads.py**: CRUD de threads + estado y mensajes
- **runs.py**: Creación y gestión de ejecuciones
- **system.py**: Health check, info, root

### **app/services/**

Lógica de negocio separada de los endpoints:

- **database.py**: Almacenamiento en memoria (InMemoryDatabase)
- **assistant_service.py**: Operaciones de assistants
- **thread_service.py**: Operaciones de threads
- **run_service.py**: Ejecución de runs
- **agent_service.py**: Integración con el agente CTM

### **templates/**

- **playground.html**: Interfaz web interactiva con diseño moderno

## 🔄 Flujo de Datos

```
Request → Router → Service → Agent/Database → Service → Router → Response
```

1. **Router** recibe la request y valida con Pydantic
2. **Service** ejecuta la lógica de negocio
3. **Agent/Database** procesa o almacena datos
4. **Service** formatea la respuesta
5. **Router** retorna la respuesta validada

## 🎨 Características del Diseño

### **Separación de Responsabilidades**

- **Models**: Solo definición de datos
- **Routers**: Solo manejo de HTTP
- **Services**: Solo lógica de negocio

### **Modularidad**

Cada componente es independiente y puede ser:
- Testeado por separado
- Reemplazado sin afectar otros
- Extendido fácilmente

### **Escalabilidad**

- Fácil agregar nuevos endpoints
- Fácil cambiar la base de datos
- Fácil agregar middleware

## 📊 Endpoints por Categoría

### Assistants (7 endpoints)
```
POST   /assistants
POST   /assistants/search
GET    /assistants
GET    /assistants/{assistant_id}
PATCH  /assistants/{assistant_id}
DELETE /assistants/{assistant_id}
POST   /assistants/{assistant_id}/latest
```

### Threads (8 endpoints)
```
POST   /threads
GET    /threads
GET    /threads/{thread_id}
PATCH  /threads/{thread_id}
DELETE /threads/{thread_id}
GET    /threads/{thread_id}/state
GET    /threads/{thread_id}/messages
POST   /threads/{thread_id}/state/checkpoint
```

### Runs (6 endpoints)
```
POST   /threads/{thread_id}/runs
POST   /threads/{thread_id}/runs/wait  ⭐ Principal
GET    /threads/{thread_id}/runs
GET    /threads/{thread_id}/runs/{run_id}
POST   /threads/{thread_id}/runs/{run_id}/cancel
POST   /threads/{thread_id}/runs/stream
```

### System (3 endpoints)
```
GET    /
GET    /ok
GET    /info
```

**Total: 24 endpoints**

## 🚀 Próximos Pasos Sugeridos

1. **Persistencia**: Reemplazar InMemoryDatabase con PostgreSQL/MongoDB
2. **Autenticación**: Agregar JWT o API Keys
3. **Rate Limiting**: Limitar requests por usuario
4. **Caching**: Redis para mejorar performance
5. **Logging**: Sistema de logs estructurado
6. **Monitoring**: Prometheus + Grafana
7. **Tests**: Unit tests y integration tests
8. **Docker**: Containerización para deployment
9. **CI/CD**: Pipeline de deployment automático
10. **WebSockets**: Streaming real-time de eventos

---

**Versión**: 0.1.0  
**Última actualización**: 2025-10-16
