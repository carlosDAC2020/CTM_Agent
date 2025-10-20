# Agente de Inversión CTM - Guía de Interacción con la API

Este documento describe el protocolo de comunicación y la lógica necesaria para interactuar de forma genérica y robusta con el Agente de Inversión CTM a través de su API local de LangGraph. Los principios aquí descritos son aplicables para la construcción de cualquier tipo de cliente (aplicación web, script de backend, herramienta de línea de comandos, etc.).

## Visión General de la Arquitectura de Comunicación

El agente está diseñado como un **sistema estado-respuesta basado en interrupciones**. A diferencia de una API REST tradicional donde cada petición tiene una respuesta final, la interacción con este agente es un **diálogo continuo** dentro de un "hilo" de conversación.

El flujo de comunicación se basa en dos conceptos clave:
1.  **Sondeo de Estado (Polling):** El cliente inicia tareas en el agente y luego pregunta periódicamente por el estado del hilo de conversación para saber cuándo ha terminado una tarea o si necesita intervención del usuario.
2.  **Manejo de Interrupciones:** Cuando el agente necesita información del usuario (por ejemplo, para seleccionar oportunidades o hacer una pregunta), "pausa" su ejecución y lo señala a través de una **interrupción** en el estado del hilo.

## El Protocolo de Interacción en 4 Pasos

Cualquier cliente que desee comunicarse con el agente debe seguir este ciclo de vida:

### Paso 1: Creación del Hilo de Conversación

Toda evaluación de un proyecto se realiza dentro de un **hilo** (`thread`) aislado. Este es el primer paso obligatorio.

*   **Endpoint:** `POST /threads`
*   **Acción del Cliente:** Enviar una petición POST a `http://127.0.0.1:2024/threads` con un cuerpo JSON vacío (`{}`).
*   **Respuesta Esperada:** Un objeto JSON que contiene el `thread_id`.
    ```json
    {
      "thread_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      ...
    }
    ```
*   **Lógica del Cliente:** El cliente **debe almacenar este `thread_id`**, ya que será utilizado en todas las comunicaciones posteriores para esta sesión de evaluación.

### Paso 2: Inicio de la Ejecución en Segundo Plano

Una vez que se tiene un hilo, el cliente inicia la evaluación del proyecto. Es crucial entender que esta petición no espera a que el agente termine; simplemente le "da la orden" de empezar.

*   **Endpoint:** `POST /threads/{thread_id}/runs`
*   **Acción del Cliente:** Enviar una petición POST a este endpoint, reemplazando `{thread_id}`. El cuerpo de la petición debe usar la clave `"input"` para proporcionar los datos iniciales.
    ```json
    {
        "assistant_id": "agent",
        "input": {
            "project_title": "Título de tu proyecto",
            "project_description": "Descripción detallada de tu proyecto."
        }
    }
    ```
*   **Respuesta Esperada:** Una confirmación de que la tarea ha sido iniciada.
*   **Lógica del Cliente:** Inmediatamente después de recibir la confirmación, el cliente debe **comenzar el sondeo de estado** (Paso 3).

### Paso 3: Sondeo de Estado y Detección de Interrupciones (El Corazón de la Lógica)

Este es el paso más importante. El cliente entra en un bucle donde pregunta periódicamente por el estado del hilo hasta que detecta una pausa.

*   **Endpoint:** `GET /threads/{thread_id}/state`
*   **Lógica del Cliente:**
    1.  Implementar un bucle (por ejemplo, `setInterval` en JavaScript o un `while` con `time.sleep` en Python) que se ejecute cada 2-3 segundos.
    2.  En cada iteración, realizar una petición GET al endpoint de estado.
    3.  Analizar la respuesta JSON y **buscar la clave `interrupts`**.
        *   **Si `interrupts` está vacía (`[]`)**: El agente sigue trabajando. El cliente puede opcionalmente leer otros campos del estado (como `search_queries`, `search_results`) para mostrar el progreso en tiempo real en la interfaz. El bucle continúa.
        *   **Si `interrupts` NO está vacía**: ¡El agente se ha detenido! El cliente debe:
            a. **Detener el bucle de sondeo** (`clearInterval` o romper el `while`).
            b. **Procesar la interrupción** y pasar al Paso 4.

### Paso 4: Reanudación de la Ejecución (Manejo de la Interrupción)

Cuando se detecta una interrupción, el cliente debe actuar.

*   **Endpoint:** `POST /threads/{thread_id}/runs` (el mismo que en el Paso 2).
*   **Lógica del Cliente:**
    1.  **Analizar el contenido de la interrupción:** El objeto `interrupts[0].value` contiene la información que el agente está solicitando (la lista de oportunidades, el prompt del chat, etc.).
    2.  **Presentar la información al usuario:** Mostrar la interfaz correspondiente (una lista de checkboxes para las oportunidades, un campo de texto para el chat).
    3.  **Recopilar la entrada del usuario:** Obtener el valor que el usuario ha proporcionado (ej. `[0, 2]` o `"Mi pregunta..."`).
    4.  **Construir el payload de reanudación:** Este es el punto más crítico. El cuerpo de la petición **debe** usar la estructura `"command": {"resume": ...}`.
        ```json
        // Ejemplo para reanudar la selección
        {
            "assistant_id": "agent",
            "command": {
                "resume":
            }
        }

        // Ejemplo para reanudar el chat
        {
            "assistant_id": "agent",
            "command": {
                "resume": "Mi pregunta para el agente."
            }
        }
        ```
    5.  Enviar esta petición POST para reanudar la ejecución del agente.
    6.  **Volver al Paso 3:** Inmediatamente después de enviar el comando de reanudación, el cliente debe **reiniciar el bucle de sondeo de estado** para esperar la siguiente interrupción o el final del proceso.

## Diagrama de Flujo del Cliente

```mermaid
graph TD
    A[Inicio] --> B{1. Crear Hilo};
    B --> C[Almacenar thread_id];
    C --> D{2. Iniciar Ejecución con "input"};
    D --> E{3. Iniciar Sondeo de Estado (cada 2s)};
    E --> F{¿Respuesta de estado contiene 'interrupts' no vacío?};
    F -- No --> E;
    F -- Sí --> G{Detener Sondeo};
    G --> H{4. Analizar interrupción y mostrar UI al usuario};
    H --> I[Recopilar entrada del usuario];
    I --> J{Construir payload con "command:resume"};
    J --> K[Enviar payload para reanudar];
    K --> E;
```


