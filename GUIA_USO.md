# 🚀 Guía de Uso - Cliente Mejorado del Agente CTM

## Resumen

El cliente de prueba del Agente CTM ahora incluye capacidades avanzadas para gestionar proyectos, reanudar ejecuciones anteriores y realizar acciones contextuales basadas en el estado de cada thread.

---

## 🎯 Características Principales

### 1. **Selección de Proyectos desde Base de Datos**

Al iniciar el cliente, puedes:
- Ver todos los proyectos disponibles en `projects_database.json`
- Seleccionar un proyecto existente para investigación
- Crear un proyecto personalizado
- Ver el historial de threads anteriores

**Ejemplo:**
```
📁 BASE DE DATOS DE PROYECTOS

[0] Sistema de Energía Solar para Comunidades Rurales
    📂 Categoría: Energía Renovable
    💰 Presupuesto: $250,000
    ⏱️  Duración: 18 meses
    🏷️  Tags: energía solar, sostenibilidad, comunidades rurales...

[1] Plataforma de Telemedicina con IA
    📂 Categoría: Salud Digital
    💰 Presupuesto: $500,000
    ...

[C] Crear proyecto personalizado
[H] Ver historial de threads
[Q] Salir
```

---

### 2. **Historial de Threads**

El sistema guarda automáticamente todas las ejecuciones en `threads_history.json`.

**Información guardada:**
- ID del thread y asistente
- Proyecto investigado
- Fecha y duración de ejecución
- Oportunidades encontradas y seleccionadas
- Estado del reporte
- Número de interacciones en chat

**Acceso:**
Desde el menú principal, presiona `[H]` para ver el historial.

---

### 3. **Reanudar Threads Anteriores**

Puedes retomar cualquier investigación anterior desde donde la dejaste.

**El sistema detecta automáticamente:**
- Si quedaste en la selección de oportunidades
- Si estabas en modo chat
- Si el reporte ya está completo
- Si el análisis está en progreso

**Menú contextual inteligente:**
```
🎯 ACCIONES DISPONIBLES PARA ESTE THREAD

⏸️  El thread está esperando SELECCIÓN DE OPORTUNIDADES
   💼 8 oportunidades encontradas

📋 Opciones:
   [1] Seleccionar oportunidades
   [2] Ver estado completo del thread
   [3] Ver oportunidades encontradas
   [0] Cancelar y volver al menú
```

---

### 4. **Selección Mejorada de Oportunidades**

Cuando el agente encuentra oportunidades de financiación, puedes:

**Opciones de selección:**
- Seleccionar específicas: `0,1,2`
- Seleccionar todas: `all`
- No seleccionar ninguna: `none`
- Volver al menú: `back` (solo al reanudar)

**Información mostrada:**
- Nombre de la organización
- Descripción de la oportunidad
- Tipo de financiación
- Fecha límite
- URL de la convocatoria

**Ejemplo:**
```
  [0] Horizon Europe
      📋 Funding for renewable energy projects...
      💰 Tipo: Grant | 📅 Deadline: 2025-12-31
      🔗 https://ec.europa.eu/info/funding-tenders/...

👉 Tu selección: 0,2,5
✅ Seleccionaste 3 oportunidades: [0, 2, 5]
```

---

### 5. **Modo Chat Interactivo**

Una vez generado el reporte, puedes hacer preguntas sobre:
- El proyecto y sus componentes
- Las oportunidades de financiación
- Las recomendaciones del reporte
- La propuesta conceptual
- Implementación de mejoras
- Alineación con oportunidades

**Ejemplos de preguntas:**
- "¿Cuáles son las mejores oportunidades para mi proyecto?"
- "¿Cómo puedo implementar las recomendaciones del reporte?"
- "¿Qué requisitos tienen las oportunidades seleccionadas?"
- "¿Cuál es el presupuesto estimado para implementar las mejoras?"

**Finalizar chat:**
Escribe `end`, `fin`, `finalizar`, `salir` o `exit`

---

### 6. **Ver Oportunidades con Estado**

Puedes revisar todas las oportunidades encontradas con indicadores visuales:
- ✅ = Oportunidad seleccionada
- ⬜ = Oportunidad no seleccionada

**Incluye:**
- Descripción completa
- Tipo de financiación
- Fecha límite
- URL completa

---

### 7. **Ver Extracto del Reporte**

Revisa un extracto del reporte generado sin entrar al modo chat.

**Muestra:**
- Longitud total del reporte
- Primeros 1000 caracteres
- Sugerencia para explorar en chat

---

### 8. **Detalles Completos del Thread**

Obtén información detallada de cualquier thread:
- IDs de thread y asistente
- Proyecto investigado
- Fecha de creación
- Duración de ejecución
- Métricas de oportunidades
- Estado del reporte
- Total de interacciones

---

## 📋 Flujos de Trabajo Comunes

### Flujo 1: Investigación Nueva

1. Ejecuta: `python test_agent.py`
2. Selecciona un proyecto: `0`
3. Espera el descubrimiento de oportunidades
4. Selecciona oportunidades: `0,1,2`
5. Espera la generación del reporte
6. Haz preguntas en modo chat
7. Finaliza: `end`

### Flujo 2: Continuar Chat Anterior

1. Ejecuta: `python test_agent.py`
2. Ver historial: `H`
3. Reanudar thread: `R` → `0`
4. Selecciona acción: `1` (Continuar chat)
5. Haz más preguntas
6. Finaliza: `end`

### Flujo 3: Cambiar Selección de Oportunidades

1. Ejecuta: `python test_agent.py`
2. Ver historial: `H`
3. Reanudar thread: `R` → `1`
4. Ver oportunidades: `3`
5. Seleccionar oportunidades: `1` → `0,2,4`
6. Continúa con el análisis

### Flujo 4: Explorar sin Reanudar

1. Ejecuta: `python test_agent.py`
2. Ver historial: `H`
3. Ver detalles: `D` → `0`
4. Revisa la información
5. Vuelve: `V`

---

## 🎨 Indicadores Visuales

El cliente usa emojis para mejor experiencia:

| Emoji | Significado |
|-------|-------------|
| ✅ | Completado/Seleccionado |
| ⏸️ | Pausado/Esperando |
| 🔄 | Reanudando/Continuando |
| ⬜ | No seleccionado |
| 💼 | Oportunidades |
| 📄 | Reporte |
| 💬 | Chat/Interacciones |
| 🔍 | Buscando/Analizando |
| ⚠️ | Advertencia |
| ❌ | Error/Inválido |
| 🎯 | Acciones/Menú |
| 📊 | Datos/Estadísticas |

---

## 🔧 Configuración Requerida

### Variables de Entorno

Asegúrate de tener configuradas:
```bash
GEMINI_API_KEY=tu_clave_aquí
TAVILY_API_KEY=tu_clave_aquí
BRAVE_SEARCH_API_KEY=tu_clave_aquí  # Opcional
```

### Servidor LangGraph

El servidor debe estar corriendo:
```bash
# En el directorio ctm-investment-agent
langgraph dev
```

Verifica que esté accesible en: `http://127.0.0.1:2024`

---

## 💡 Consejos y Mejores Prácticas

1. **Revisa el historial** antes de iniciar una nueva investigación del mismo proyecto
2. **Usa el menú contextual** para entender qué acciones están disponibles
3. **Visualiza las oportunidades** antes de seleccionar para tomar decisiones informadas
4. **Aprovecha el modo chat** para explorar a fondo el reporte generado
5. **Guarda los IDs** de threads importantes para referencia futura
6. **Selecciona oportunidades relevantes** en lugar de todas, para análisis más enfocado

---

## 🐛 Solución de Problemas

### Thread no encontrado al reanudar
**Causa:** El thread fue eliminado del servidor LangGraph  
**Solución:** Verifica que el servidor esté corriendo y que el thread no haya expirado

### No se encuentran oportunidades
**Causa:** Claves API no configuradas o sin conectividad  
**Solución:** 
- Verifica las variables de entorno
- Confirma conexión a internet
- Revisa que la descripción del proyecto sea clara

### Modo chat no disponible
**Causa:** El reporte no se ha generado  
**Solución:**
- Asegúrate de que el análisis académico se completó
- Verifica que seleccionaste al menos una oportunidad
- Revisa los logs del agente

### Error al seleccionar oportunidades
**Causa:** Índices inválidos  
**Solución:** El sistema filtra automáticamente índices inválidos, pero asegúrate de usar números dentro del rango mostrado

---

## 📚 Archivos Importantes

- `test_agent.py` - Cliente principal
- `projects_database.json` - Base de datos de proyectos
- `threads_history.json` - Historial de ejecuciones
- `ENHANCED_FEATURES.md` - Documentación completa en inglés
- `ARCHITECTURE_DIAGRAM.md` - Diagrama de arquitectura

---

## 🎓 Recursos Adicionales

Para más información:
- Revisa `QUICKSTART.md` para instrucciones de instalación
- Consulta `contxt/` para documentos de contexto
- Lee `ARCHITECTURE_DIAGRAM.md` para entender el diseño del sistema

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs del agente
2. Verifica que todas las APIs estén configuradas
3. Confirma que el servidor LangGraph esté corriendo
4. Consulta la documentación técnica

---

**Versión**: 2.0  
**Última Actualización**: 16 de Octubre, 2025  
**Equipo**: CTM Agent Development Team
