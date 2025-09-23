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
    
    # Handler para heartbeats (rotación diaria)
    heartbeats_file_handler = TimedRotatingFileHandler(
        os.path.join(LOGS_DIR, 'monitor_heartbeats.log'),
        when='midnight',
        interval=1,
        backupCount=7  # Solo 7 días de heartbeats
    )
    heartbeats_file_handler.setLevel(logging.DEBUG)
    heartbeats_file_formatter = logging.Formatter(
        '%(asctime)s - HEARTBEAT - %(message)s',
        date_format
    )
    heartbeats_file_handler.setFormatter(heartbeats_file_formatter)
    
    # Logger específico para heartbeats
    heartbeat_logger = logging.getLogger('monitor.heartbeats')
    heartbeat_logger.setLevel(logging.DEBUG)
    heartbeat_logger.addHandler(heartbeats_file_handler)
    heartbeat_logger.propagate = False  # No propagar al logger padre
    
    return logger

# Configurar logging
logger = setup_logging()

# Configure logging básico (para compatibilidad)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

ULTIMOS_HEARTBEATS = {}
LATENCIAS = {}
SERVICIOS_MONITOREADOS = ['modulo-pedidos-1', 'modulo-pedidos-2', 'modulo-pedidos-3']
SCHEDULER_INTERVAL_SECONDS = int(os.environ.get('SCHEDULER_INTERVAL_SECONDS', 3))


@app.route('/')
def home():
    return jsonify({"mensaje": "Hola, soy el microservicio Monitor!"})

@app.route('/reportar-heartbeat', methods=['POST'])
def reportar_heartbeat():
    data = request.json
    if not data:
        logger.error("Request body vacío o no JSON")
        return jsonify({"status": "error", "mensaje": "Request body debe ser JSON"}), 400

    servicio_origen = data.get('servicio_origen', 'desconocido')
    timestamp_str = data.get('timestamp')

    if not timestamp_str:
        logger.error(f"Heartbeat de '{servicio_origen}' sin timestamp")
        return jsonify({"status": "error", "mensaje": "Falta el timestamp"}), 400

    # Comparar la fecha que llega con la fecha actual
    try:
        # El timestamp viene en formato ISO 8601 con timezone
        timestamp_origen = datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError) as e:
        logger.error(f"Formato de timestamp inválido de '{servicio_origen}': {timestamp_str}. Error: {e}")
        return jsonify({"status": "error", "mensaje": "Formato de timestamp inválido"}), 400

    ahora_utc = datetime.now(timezone.utc)
    latencia = ahora_utc - timestamp_origen

    # Guardar ultimo heartbeat y latencia
    ULTIMOS_HEARTBEATS[servicio_origen] = ahora_utc
    LATENCIAS[servicio_origen] = latencia.total_seconds()

    # Log específico para heartbeats (archivo separado)
    heartbeat_logger = logging.getLogger('monitor.heartbeats')
    heartbeat_logger.info(f"Servicio: {servicio_origen} | Latencia: {latencia.total_seconds():.4f}s | Timestamp: {timestamp_str}")
    
    # Log general
    logger.info(f"✅ Heartbeat recibido de '{servicio_origen}' - Latencia: {latencia.total_seconds():.4f}s")
    
    return jsonify({
        "status": "OK",
        "servicio_origen": servicio_origen,
        "latencia_segundos": latencia.total_seconds()
    }), 200


def monitor():
    """
    Función que se ejecuta periódicamente para monitorear los servicios.
    """
    logger.debug(f"Ejecutando monitoreo de {len(SERVICIOS_MONITOREADOS)} servicios")
    
    ahora = datetime.now(timezone.utc)
    servicios_con_problemas = []
    
    for servicio in SERVICIOS_MONITOREADOS:
        ultimo_heartbeat = ULTIMOS_HEARTBEATS.get(servicio)
        
        if ultimo_heartbeat:
            tiempo_desde_ultimo = (ahora - ultimo_heartbeat).total_seconds()
            
            if tiempo_desde_ultimo > SCHEDULER_INTERVAL_SECONDS * 2:
                mensaje_alerta = f"Servicio '{servicio}' sin heartbeat por {tiempo_desde_ultimo:.2f} segundos (último: {ultimo_heartbeat.isoformat()})"
                logger.warning(f"⚠️ ALERTA: {mensaje_alerta}")
                servicios_con_problemas.append({
                    'servicio': servicio,
                    'problema': 'timeout',
                    'tiempo_sin_heartbeat': tiempo_desde_ultimo,
                    'ultimo_heartbeat': ultimo_heartbeat.isoformat()
                })
            else:
                logger.debug(f"✅ Servicio '{servicio}' OK - último heartbeat hace {tiempo_desde_ultimo:.1f}s")
        else:
            mensaje_alerta = f"Servicio '{servicio}' nunca ha enviado heartbeat"
            logger.warning(f"⚠️ ALERTA: {mensaje_alerta}")
            servicios_con_problemas.append({
                'servicio': servicio,
                'problema': 'sin_heartbeat',
                'tiempo_sin_heartbeat': None,
                'ultimo_heartbeat': None
            })
    
    # Log de resumen del monitoreo
    if servicios_con_problemas:
        logger.warning(f"🚨 Monitoreo completado: {len(servicios_con_problemas)} servicios con problemas de {len(SERVICIOS_MONITOREADOS)} totales")
    else:
        logger.info(f"✅ Monitoreo completado: Todos los servicios ({len(SERVICIOS_MONITOREADOS)}) funcionando correctamente")


scheduler = BackgroundScheduler()
scheduler.add_job(monitor, 'interval', seconds=SCHEDULER_INTERVAL_SECONDS, id='monitor_job')
scheduler.start()

logger.info("="*50)
logger.info("🚀 MONITOR DE SERVICIOS INICIADO")
logger.info(f"📁 Directorio de logs: {LOGS_DIR}")
logger.info(f"⏱️  Intervalo de monitoreo: {SCHEDULER_INTERVAL_SECONDS} segundos")
logger.info(f"🎯 Servicios monitoreados: {', '.join(SERVICIOS_MONITOREADOS)}")
logger.info(f"🌐 Servidor Flask iniciando en puerto 5000")
logger.info("="*50)


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        logger.info("👋 Cerrando monitor de servicios...")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"💥 Error fatal en la aplicación: {e}")
        scheduler.shutdown()
        raise
