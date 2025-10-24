FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# El puerto que expondrá Daphne (servidor ASGI)
EXPOSE 8001

# Comando para iniciar el servidor. Asume que tu proyecto Django se llama 'core'
# y está dentro de un subdirectorio con el mismo nombre.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "config.asgi:application"]