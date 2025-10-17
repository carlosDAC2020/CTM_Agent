import http.client
import json
import time
from urllib.parse import urlparse

# --- Configuración ---
LANGGRAPH_API_URL = "http://127.0.0.1:2024"
POLLING_INTERVAL_SECONDS = 3

# --- Variables Globales ---
ASSISTANT_ID = None
THREAD_ID = None

# --- Funciones de Utilidad (sin cambios) ---

def get_connection():
    parsed_url = urlparse(LANGGRAPH_API_URL)
    port = parsed_url.port if parsed_url.port else 80
    return http.client.HTTPConnection(parsed_url.hostname, port)

conn = get_connection()

payload = "{\"thread_id\":\"\",\"metadata\":{},\"if_exists\":\"raise\",\"ttl\":{\"strategy\":\"delete\",\"ttl\":1},\"supersteps\":[{\"updates\":[{\"values\":[{}],\"command\":{\"update\":null,\"resume\":null,\"goto\":{\"node\":\"\",\"input\":null}},\"as_node\":\"\"}]}]}"

headers = { 'Content-Type': "application/json" }

conn.request("POST", "/threads", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))