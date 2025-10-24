esquema de reporte 

marco teorico 
estado del arte 
referneicas bibliograficas 

ejemplo de proyetco 

titulo
Poseidón AUV: Plataforma Robótica Autónoma para Inspección y Mantenimiento de Infraestructura Submarina

descripcion
Desarrollo de un Vehículo Autónomo Submarino (AUV) de nueva generación, denominado "Poseidón", diseñado para la inspección, mapeo y mantenimiento predictivo de infraestructuras críticas sumergidas, como oleoductos, cables submarinos, cimientos de parques eólicos marinos y estructuras portuarias.

El sistema se basa en tres componentes tecnológicos clave:

1.  **Hardware y Sistema de Sensores Avanzados:**
    - Un AUV modular capaz de operar a profundidades de hasta 500 metros durante misiones de 24 horas.
    - Integración de un conjunto de sensores de alta resolución:
        - **Sonar de Barrido Lateral y Multihaz:** para la creación de modelos 3D de alta definición del lecho marino y las estructuras.
        - **Cámaras 4K y Sensores Ópticos:** para la inspección visual detallada.
        - **Sensores de Corrosión Electromagnética:** para la detección no invasiva del desgaste en tuberías metálicas.
    - Un brazo robótico de precisión para realizar tareas de mantenimiento menores y toma de muestras.

2.  **Software de Navegación y Percepción Autónoma (IA a Bordo):**
    - Implementación de algoritmos de **Navegación Autónoma Basada en SLAM** (Simultaneous Localization and Mapping), permitiendo al AUV operar sin necesidad de GPS y construir mapas precisos de su entorno.
    - Desarrollo de un sistema de **Detección de Anomalías mediante Computer Vision**, entrenado para identificar automáticamente signos de corrosión, fisuras, bioincrustaciones (biofouling) y daños estructurales en las imágenes capturadas.

3.  **Plataforma de Gemelo Digital y Análisis Predictivo (En Tierra):**
    - Los datos recopilados por el AUV se utilizan para alimentar un "Gemelo Digital" de la infraestructura inspeccionada.
    - Se aplicarán modelos de Machine Learning sobre los datos históricos y en tiempo real para predecir la tasa de degradación de los materiales y recomendar proactivamente ventanas de mantenimiento, pasando de un modelo reactivo a uno predictivo.

**Objetivos Cuantificables:**
- Reducir los costos de inspección submarina en un 40% en comparación con los métodos tradicionales (buzos y ROVs operados remotamente).
- Aumentar la frecuencia de las inspecciones en un 300%, mejorando la seguridad y la detección temprana de fallos.
- Mejorar la precisión en la detección de defectos estructurales en un 50%.

**Mercado y Relevancia:**
Este proyecto aborda una necesidad crítica en los sectores de energía offshore (petróleo, gas y eólica), telecomunicaciones (cables submarinos) y acuicultura. Proporciona una solución más segura, económica y eficiente que los métodos actuales, reduciendo el riesgo para los buzos humanos y optimizando la vida útil de infraestructuras multimillonarias.

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
