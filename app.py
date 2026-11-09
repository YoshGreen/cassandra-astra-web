import os
import uuid
from datetime import datetime, timezone
import requests
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Parámetros leídos de las Variables de Entorno en Render
ASTRA_DB_URL = os.environ.get(
    "ASTRA_DB_URL", 
    "https://d079b15c-e0df-447d-bb97-5be8dcd7a8bb-us-east-2.apps.astra.datastax.com"
)
ASTRA_DB_TOKEN = os.environ.get(
    "ASTRA_DB_TOKEN", 
    "AstraCS:jscEAjDekMWWguAWvaDAwMyW:034819eaba4e591bff67fc4f08573cead5ef2fe605f24745541a3beaf7407995"
)

KEYSPACE = os.environ.get("KEYSPACE", "practica")
TABLE = os.environ.get("TABLE", "usuarios")

BASE_API_URL = f"{ASTRA_DB_URL.rstrip('/')}/api/rest/v2/keyspaces/{KEYSPACE}/{TABLE}"
HEADERS = {
    "X-Cassandra-Token": ASTRA_DB_TOKEN,
    "Content-Type": "application/json"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    error_msg = None

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if nombre:
            nuevo_registro = {
                "id": str(uuid.uuid4()),
                "nombre": nombre,
                "fecha": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
            try:
                r = requests.post(BASE_API_URL, json=nuevo_registro, headers=HEADERS, timeout=10)
                if r.status_code in (200, 201):
                    return redirect(url_for('index', exito=1))
                else:
                    error_msg = f"Código {r.status_code}: {r.text}"
            except Exception as e:
                error_msg = str(e)

    exito = request.args.get('exito')
    usuarios = []

    try:
        res = requests.get(f"{BASE_API_URL}/rows", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            usuarios = res.json().get('data', [])
            usuarios.sort(key=lambda x: x.get('fecha', ''), reverse=True)
        else:
            error_msg = f"No se pudo leer la tabla ({res.status_code}): {res.text}"
    except Exception as e:
        error_msg = str(e)

    return render_template('index.html', usuarios=usuarios, exito=exito, error=error_msg)

if __name__ == '__main__':
    # Render asigna dinámicamente el puerto en la variable PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
