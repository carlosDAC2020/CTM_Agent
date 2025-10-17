# 🚀 Quick Start Guide

Guía rápida para poner en marcha la API CTM Investment Agent en menos de 5 minutos.

## ⚡ Inicio Rápido (3 pasos)

### 1. Instalar Dependencias

```bash
cd api_ctm_agent
pip install -r requirements.txt
```

### 2. Iniciar el Servidor

```bash
python run.py
```

Verás algo como:
```
======================================================================
🚀 Iniciando CTM Investment Agent API Server
======================================================================

📝 Documentación interactiva: http://localhost:8000/docs
🎮 Playground: http://localhost:8000/playground
📊 ReDoc: http://localhost:8000/redoc
🔧 Info del servidor: http://localhost:8000/info

======================================================================
```

### 3. Probar la API

**Opción A - Playground (Recomendado):**
1. Abre tu navegador en: http://localhost:8000/playground
2. Haz clic en "Create Assistant" → Send Request
3. Haz clic en "Create Thread" → Send Request
4. Haz clic en "Run & Wait" → Completa los campos → Send Request

**Opción B - Script de Ejemplo:**
```bash
python example_usage.py
```

**Opción C - Prueba Rápida:**
```bash
python quick_test.py
```

**Opción D - cURL:**
```bash
# Health check
curl http://localhost:8000/ok

# Crear assistant
curl -X POST http://localhost:8000/assistants \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "agent", "name": "My Agent"}'
```

## 🎯 Uso Básico

### Flujo Completo en Python

```python
import requests

API = "http://localhost:8000"

# 1. Crear Assistant
assistant = requests.post(f"{API}/assistants", json={
    "graph_id": "agent",
    "name": "CTM Agent"
}).json()

assistant_id = assistant["assistant_id"]

# 2. Crear Thread
thread = requests.post(f"{API}/threads", json={}).json()
thread_id = thread["thread_id"]

# 3. Ejecutar Agente
result = requests.post(
    f"{API}/threads/{thread_id}/runs/wait",
    json={
        "assistant_id": assistant_id,
        "input": {
            "project_title": "Mi Proyecto",
            "project_description": "Análisis de inversión en tecnología",
            "messages": []
        }
    }
).json()

print(result)
```

### Flujo Completo en JavaScript

```javascript
const API = "http://localhost:8000";

async function runAgent() {
  // 1. Crear Assistant
  const assistant = await fetch(`${API}/assistants`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      graph_id: "agent",
      name: "CTM Agent"
    })
  }).then(r => r.json());

  // 2. Crear Thread
  const thread = await fetch(`${API}/threads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  }).then(r => r.json());

  // 3. Ejecutar Agente
  const result = await fetch(
    `${API}/threads/${thread.thread_id}/runs/wait`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assistant_id: assistant.assistant_id,
        input: {
          project_title: "Mi Proyecto",
          project_description: "Análisis de inversión",
          messages: []
        }
      })
    }
  ).then(r => r.json());

  console.log(result);
}

runAgent();
```

## 📚 Recursos

- **Documentación Completa**: [README.md](README.md)
- **Estructura del Proyecto**: [STRUCTURE.md](STRUCTURE.md)
- **Swagger UI**: http://localhost:8000/docs
- **Playground**: http://localhost:8000/playground

## 🔧 Configuración

### Cambiar Puerto

Edita `run.py`:
```python
uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8080,  # Cambia aquí
    reload=True
)
```

### Modo Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## ❓ Troubleshooting

### Error: "No module named 'app'"

```bash
# Asegúrate de estar en el directorio correcto
cd api_ctm_agent
python run.py
```

### Error: "Address already in use"

El puerto 8000 está ocupado. Opciones:
1. Detén el proceso que usa el puerto 8000
2. Cambia el puerto en `run.py`

### Error: "Connection refused"

El servidor no está corriendo. Ejecuta:
```bash
python run.py
```

### El agente no responde correctamente

La API funciona en modo simulado si el agente CTM no está disponible. 
Verifica que el directorio `ctm-investment-agent` esté en la ubicación correcta.

## 🎮 Playground - Guía Rápida

1. **Crear Assistant**:
   - Sidebar → "Create Assistant"
   - Click "Send Request"
   - Copia el `assistant_id` de la respuesta

2. **Crear Thread**:
   - Sidebar → "Create Thread"
   - Click "Send Request"
   - Copia el `thread_id` de la respuesta

3. **Ejecutar Agente**:
   - Sidebar → "Run & Wait"
   - Pega `thread_id` y `assistant_id`
   - Completa Project Title y Description
   - Click "Send Request"
   - Espera la respuesta del agente

## 💡 Tips

- Los IDs se auto-completan en el playground después de crear assistants/threads
- Usa "Quick Actions" para cargar ejemplos predefinidos
- Presiona "Copy as cURL" para obtener el comando equivalente
- El servidor tiene hot-reload activado (se reinicia al cambiar código)

## 🚦 Verificación

Ejecuta el test rápido para verificar que todo funciona:

```bash
python quick_test.py
```

Deberías ver:
```
📊 Results: X/X tests passed (100.0%)
🎉 All tests passed! API is working correctly.
```

---

**¿Listo para empezar?** → `python run.py` 🚀
