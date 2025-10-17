# 🚀 CTM Investment Agent - Proyecto Completo

Sistema completo de análisis inteligente de oportunidades de inversión con agente LangGraph e interfaz web.

## 📦 Componentes

### 1. **ctm-investment-agent/** 
Agente inteligente construido con LangGraph que:
- 🔍 Busca oportunidades de inversión en múltiples fuentes
- 📚 Investiga papers académicos relevantes
- 📊 Genera reportes de mejoras y recomendaciones
- 💬 Interactúa mediante chat

### 2. **ctm-web-ui/**
Interfaz web simple (HTML/CSS/JS) que:
- 📝 Gestiona proyectos de inversión
- 👁️ Visualiza el flujo del agente en tiempo real
- ✅ Permite selección dinámica de oportunidades
- 💬 Integra chat con el agente

## 🚀 Inicio Rápido (1 minuto)

### Opción 1: Script Automático (Windows)

```bash
# Doble clic en:
INICIAR_TODO.bat
```

Esto iniciará:
1. Servidor LangGraph en puerto 2024
2. Interfaz web en puerto 8080
3. Abrirá el navegador automáticamente

### Opción 2: Manual

**Terminal 1 - Agente:**
```bash
cd ctm-investment-agent
langgraph dev
```

**Terminal 2 - Interfaz:**
```bash
cd ctm-web-ui
python -m http.server 8080
```

**Navegador:**
```
http://localhost:8080
```

## 📋 Requisitos Previos

### Software Necesario
- Python 3.11+
- Node.js (opcional, para alternativas de servidor)
- Git

### API Keys Requeridas

Configura en `ctm-investment-agent/.env`:

```env
# Requerido
GOOGLE_API_KEY=tu_api_key_aqui
TAVILY_API_KEY=tu_api_key_aqui

# Opcional
BRAVE_SEARCH_API_KEY=tu_api_key_aqui
LANGSMITH_API_KEY=tu_api_key_aqui
```

**Obtener API Keys:**
- Google Gemini: https://makersuite.google.com/app/apikey
- Tavily: https://tavily.com/
- Brave Search: https://brave.com/search/api/

## 📖 Guías de Uso

### Para Empezar
1. **[INICIO_RAPIDO.md](ctm-web-ui/INICIO_RAPIDO.md)** - Guía de 5 minutos
2. **[SOLUCION_COMPLETA.md](SOLUCION_COMPLETA.md)** - Documentación técnica completa

### Documentación Detallada
- **[ctm-investment-agent/README.md](ctm-investment-agent/README.md)** - Agente LangGraph
- **[ctm-web-ui/README.md](ctm-web-ui/README.md)** - Interfaz web

## 🎯 Flujo de Uso

```
1. Crear Proyecto
   ↓
2. Ejecutar Análisis
   ↓
3. Visualizar Flujo en Tiempo Real
   ├─ Ingesta de información
   ├─ Búsqueda de oportunidades
   ├─ Selección interactiva ← Usuario selecciona
   ├─ Investigación académica
   └─ Generación de reporte
   ↓
4. Ver Resultados
   ├─ Oportunidades encontradas
   ├─ Papers académicos
   └─ Reporte de mejoras
   ↓
5. Chatear con el Agente
   └─ Hacer preguntas y profundizar
```

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Navegador Web  │  ← Interfaz HTML/CSS/JS
└────────┬────────┘
         │ HTTP/SSE
┌────────▼────────┐
│ LangGraph API   │  ← Servidor en puerto 2024
│  (Puerto 2024)  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Agente CTM     │  ← Flujo de nodos LangGraph
│  (LangGraph)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  APIs Externas  │  ← Gemini, Tavily, Brave
└─────────────────┘
```

## 📁 Estructura del Proyecto

```
CTM_Agent/
├── ctm-investment-agent/       # Agente LangGraph
│   ├── src/agent/
│   │   ├── graph.py           # Definición del grafo
│   │   ├── state.py           # Estado del agente
│   │   └── nodes/             # Nodos del flujo
│   ├── langgraph.json         # Config LangGraph
│   ├── .env                   # API keys
│   └── README.md
│
├── ctm-web-ui/                 # Interfaz Web
│   ├── index.html             # HTML principal
│   ├── styles.css             # Estilos
│   ├── app.js                 # Lógica JavaScript
│   ├── serve.bat              # Script servidor
│   ├── README.md              # Docs interfaz
│   └── INICIO_RAPIDO.md       # Guía rápida
│
├── INICIAR_TODO.bat            # Script inicio automático
├── SOLUCION_COMPLETA.md        # Documentación técnica
└── README.md                   # Este archivo
```

## ✨ Características

### Agente CTM
- ✅ Búsqueda inteligente de oportunidades
- ✅ Análisis académico automatizado
- ✅ Generación de reportes personalizados
- ✅ Chat interactivo contextual
- ✅ Streaming en tiempo real

### Interfaz Web
- ✅ Gestión de proyectos (LocalStorage)
- ✅ Visualización de flujo en vivo
- ✅ Selección dinámica de oportunidades
- ✅ Resultados organizados y claros
- ✅ Chat integrado
- ✅ Sin dependencias complejas
- ✅ Responsive design

## 🎨 Ejemplo de Uso

### 1. Crear Proyecto

**Título:** Plataforma AgriTech con IoT

**Descripción:**
```
Desarrollo de plataforma de agricultura de precisión que combina:
- Drones con cámaras multiespectrales
- Sensores IoT para monitoreo de suelo
- IA para predicción de plagas
- App móvil para agricultores

Objetivos:
- Aumentar productividad 30%
- Reducir uso de agua 40%
- Disminuir pesticidas 50%

Mercado: Colombia (Antioquia, Valle, Santander)
Población: Agricultores de café, cacao, frutas
```

### 2. Resultados Esperados

El agente encontrará:
- 🎯 **Oportunidades**: Convocatorias, fondos, aceleradoras
- 📚 **Papers**: Investigación sobre AgriTech, IoT agrícola
- 📊 **Reporte**: Mejoras técnicas, estrategias de mercado

## 🔧 Configuración Avanzada

### Cambiar Puerto del Agente

Edita `ctm-investment-agent/langgraph.json`:
```json
{
  "port": 2024  // Cambia este valor
}
```

Y actualiza `ctm-web-ui/app.js`:
```javascript
const API_BASE_URL = 'http://127.0.0.1:2024'; // Nuevo puerto
```

### Personalizar Nodos del Flujo

Edita `ctm-investment-agent/src/agent/graph.py` para:
- Agregar nuevos nodos
- Modificar el flujo
- Cambiar lógica de routing

Luego actualiza `ctm-web-ui/app.js` en `NODE_INFO` para reflejar los cambios.

## 🐛 Solución de Problemas

### "Desconectado" en la interfaz
```bash
# Verifica que el agente esté corriendo
cd ctm-investment-agent
langgraph dev
```

### Error de API Keys
```bash
# Verifica el archivo .env
cd ctm-investment-agent
cat .env  # Linux/Mac
type .env  # Windows
```

### Puerto ocupado
```bash
# Cambia el puerto en langgraph.json
# O mata el proceso que usa el puerto 2024
```

### No se encuentran oportunidades
- Verifica API keys válidas
- Revisa logs del servidor LangGraph
- Confirma conexión a internet

## 📊 Monitoreo y Debugging

### Ver Logs del Agente
Los logs aparecen en la terminal donde ejecutaste `langgraph dev`

### Ver Logs de la Interfaz
Abre la consola del navegador (F12) → Console

### LangSmith (Opcional)
Para debugging avanzado, configura en `.env`:
```env
LANGSMITH_API_KEY=tu_key
LANGSMITH_TRACING=true
```

Luego visita: https://smith.langchain.com/

## 🚀 Despliegue en Producción

### Consideraciones
- ⚠️ Implementar autenticación
- ⚠️ Usar HTTPS
- ⚠️ Base de datos real (no LocalStorage)
- ⚠️ Rate limiting
- ⚠️ Logs estructurados
- ⚠️ Backups automáticos

### Opciones de Hosting
- **Agente**: Railway, Render, AWS, Google Cloud
- **Interfaz**: Netlify, Vercel, GitHub Pages
- **Todo junto**: Docker + Kubernetes

## 📈 Roadmap

### Versión 1.1
- [ ] Exportar/importar proyectos
- [ ] Historial de ejecuciones
- [ ] Modo oscuro
- [ ] Notificaciones

### Versión 2.0
- [ ] Backend con base de datos
- [ ] Autenticación de usuarios
- [ ] Colaboración multi-usuario
- [ ] API REST pública

### Versión 3.0
- [ ] Integración con calendarios
- [ ] Alertas de deadlines
- [ ] Gráficos y analytics
- [ ] Mobile app nativa

## 🤝 Contribuir

Este es un proyecto personal, pero las sugerencias son bienvenidas:
1. Reporta bugs abriendo un issue
2. Sugiere mejoras
3. Comparte casos de uso

## 📄 Licencia

Este proyecto es de uso personal/educativo.

## 🙏 Agradecimientos

- **LangGraph** - Framework para agentes
- **Google Gemini** - Modelo de lenguaje
- **Tavily** - API de búsqueda
- **Brave Search** - Búsqueda alternativa

## 📞 Soporte

- **Documentación**: Lee los archivos README en cada carpeta
- **API Docs**: http://127.0.0.1:2024/docs (cuando el servidor esté activo)
- **Guía Rápida**: [INICIO_RAPIDO.md](ctm-web-ui/INICIO_RAPIDO.md)
- **Técnica**: [SOLUCION_COMPLETA.md](SOLUCION_COMPLETA.md)

---

**¡Listo para analizar oportunidades de inversión! 🎉**

Para empezar ahora:
1. Ejecuta `INICIAR_TODO.bat` (Windows)
2. O sigue la guía en [INICIO_RAPIDO.md](ctm-web-ui/INICIO_RAPIDO.md)

**Versión**: 1.0.0  
**Última actualización**: 2024
