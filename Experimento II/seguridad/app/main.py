import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from flask import Flask, request, jsonify
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler

# Crear directorio de logs si no existe
LOGS_DIR = '/var/logs/monitor'  # Dentro del contenedor
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configurar múltiples loggers
def setup_logging():
    # Configuración base
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Logger principal
    logger = logging.getLogger('monitor')
    logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler para consola (desarrollo)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo general (rotación por tamaño)
    general_file_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, 'monitor_general.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    general_file_handler.setLevel(logging.INFO)
    general_file_formatter = logging.Formatter(log_format, date_format)
    general_file_handler.setFormatter(general_file_formatter)
    logger.addHandler(general_file_handler)
    
    # Handler para errores y alertas (rotación diaria)
    alerts_file_handler = TimedRotatingFileHandler(
        os.path.join(LOGS_DIR, 'monitor_alerts.log'),
        when='midnight',
        interval=1,
        backupCount=30
    )
    alerts_file_handler.setLevel(logging.WARNING)
    alerts_file_formatter = logging.Formatter(log_format, date_format)
    alerts_file_handler.setFormatter(alerts_file_formatter)
    logger.addHandler(alerts_file_handler)
    
    # Handler para evento (rotación diaria)
    evento_file_handler = TimedRotatingFileHandler(
        os.path.join(LOGS_DIR, 'eventos.log'),
        when='midnight',
        interval=1,
        backupCount=7  # Solo 7 días de evento
    )
    evento_file_handler.setLevel(logging.DEBUG)
    evento_file_formatter = logging.Formatter(
        '%(asctime)s - EVENTO - %(message)s',
        date_format
    )
    evento_file_handler.setFormatter(evento_file_formatter)
    
    # Logger específico para evento
    evento_logger.setLevel(logging.DEBUG)
    evento_logger.addHandler(evento_file_handler)
    evento_logger.propagate = False  # No propagar al logger padre
    
    return logger

# Configurar logging
evento_logger = logging.getLogger('evento')
logger = setup_logging()

# Configure logging básico (para compatibilidad)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

ULTIMOS_EVENTOS = {}
LATENCIAS = {}
SERVICIOS_MONITOREADOS = ['modulo-pedidos-1', 'modulo-pedidos-2', 'modulo-pedidos-3']
SCHEDULER_INTERVAL_SECONDS = int(os.environ.get('SCHEDULER_INTERVAL_SECONDS', 3))


@app.route('/reportar-evento', methods=['POST'])
def reportar_evento():
    data = request.json
    if not data:
        logger.error("Request body vacío o no JSON")
        return jsonify({"status": "error", "mensaje": "Request body debe ser JSON"}), 400

    timestamp_str = data.get('timestamp')

    if not timestamp_str:
        return jsonify({"status": "error", "mensaje": "Falta el timestamp"}), 400

    # Comparar la fecha que llega con la fecha actual
    try:
        # El timestamp viene en formato ISO 8601 con timezone
        timestamp_origen = datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError) as e:
        return jsonify({"status": "error", "mensaje": "Formato de timestamp inválido"}), 400

    ahora_utc = datetime.now(timezone.utc)
    latencia = ahora_utc - timestamp_origen

    # Guardar ultimo heartbeat y latencia
    ULTIMOS_EVENTOS["Logistica"] = ahora_utc
    LATENCIAS["Logistica"] = latencia.total_seconds()

    # Log específico para heartbeats (archivo separado)
    evento_logger.info(f"Servicio: Logistica | Latencia: {latencia.total_seconds():.4f}s | Timestamp: {timestamp_str}")
    
    # Log general
    logger.info(f"Evento recibido de Logistica - Latencia: {latencia.total_seconds():.4f}s")
    
    return jsonify({
        "status": "OK",
        "latencia_segundos": latencia.total_seconds()
    }), 200



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}")
        scheduler.shutdown()
        raise
