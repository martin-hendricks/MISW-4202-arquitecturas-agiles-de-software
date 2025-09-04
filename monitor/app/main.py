from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

ULTIMOS_HEARTBEATS = {}
LATENCIAS = {}

@app.route('/')
def home():
    return jsonify({"mensaje": "Hola, soy el microservicio Monitor!"})

@app.route('/reportar-heartbeat', methods=['POST'])
def reportar_heartbeat():
    data = request.json
    if not data:
        return jsonify({"status": "error", "mensaje": "Request body debe ser JSON"}), 400

    servicio_origen = data.get('servicio_origen', 'desconocido')
    timestamp_str = data.get('timestamp')

    if not timestamp_str:
        return jsonify({"status": "error", "mensaje": "Falta el timestamp"}), 400

    # Comparar la fecha que llega con la fecha actual
    try:
        # El timestamp viene en formato ISO 8601 con timezone
        timestamp_origen = datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "mensaje": "Formato de timestamp inválido"}), 400

    ahora_utc = datetime.now(timezone.utc)
    latencia = ahora_utc - timestamp_origen

    # Guardar ultimo heartbeat y latencia
    ULTIMOS_HEARTBEATS[servicio_origen] = ahora_utc
    LATENCIAS[servicio_origen] = latencia.total_seconds()

    logging.info(f"✅ Heartbeat recibido de '{servicio_origen}'. Latencia: {latencia.total_seconds():.4f} segundos.")
    
    return jsonify({
        "status": "OK",
        "servicio_origen": servicio_origen,
        "latencia_segundos": latencia.total_seconds()
    }), 200

@app.route('/status')
def status():
    return jsonify({
        "ultimos_heartbeats": {k: v.isoformat() for k, v in ULTIMOS_HEARTBEATS.items()},
        "latencias_segundos": LATENCIAS
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
