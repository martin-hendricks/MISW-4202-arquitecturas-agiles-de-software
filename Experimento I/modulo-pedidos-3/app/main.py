from flask import Flask, jsonify, request
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import redis
from rq import Queue
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Redis and RQ setup
redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_conn = redis.Redis(host=redis_host, port=redis_port)
q = Queue(connection=redis_conn)

# Scheduler interval configuration
SCHEDULER_INTERVAL_SECONDS = int(os.environ.get('SCHEDULER_INTERVAL_SECONDS', 3))

def encolar_tarea():
    """
    Encola una tarea en Redis.
    """
    with app.app_context():
        pedido_id = str(uuid.uuid4())
        colombia_tz = ZoneInfo("America/Bogota")
        now_colombia = datetime.now(colombia_tz)
        timestamp = now_colombia.isoformat()

        task_payload = {
            "id": pedido_id,
            "timestamp": timestamp,
            "servicio_origen": "modulo-pedidos-3"
        }

        q.enqueue('tasks.heartbeat_ping', task_payload)
        
        logging.info(f"Tarea encolada: {task_payload}")

@app.route('/')
def home():
    return jsonify({"mensaje": "Hola, soy el microservicio respaldo zona 2 de pedidos! Ahora funciono como un scheduler."})

@app.route('/shutdown', methods=['POST'])
def shutdown_scheduler():
    """
    Shuts down the component.
    """
    try:
        scheduler.shutdown()
        logging.info("component shut down via API request.")
        return jsonify({"mensaje": "component shut down successfully."}), 200
    except Exception as e:
        logging.error(f"Error shutting down component: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reschedule', methods=['POST'])
def reschedule_job():
    """
    Reschedules the task with a new interval.
    """
    data = request.get_json()
    if not data or 'interval' not in data:
        return jsonify({"error": "Missing 'interval' in request body"}), 400

    try:
        new_interval = int(data['interval'])
        if new_interval <= 0:
            raise ValueError("Interval must be a positive integer.")
            
        scheduler.reschedule_job('encolar_tarea_job', trigger='interval', seconds=new_interval)
        
        global SCHEDULER_INTERVAL_SECONDS
        SCHEDULER_INTERVAL_SECONDS = new_interval
        
        logging.info(f"Job 'encolar_tarea_job' rescheduled to run every {new_interval} seconds.")
        return jsonify({"mensaje": f"Scheduler interval updated to {new_interval} seconds."}), 200
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid interval format. Must be a positive integer."}), 400
    except Exception as e:
        logging.error(f"Error rescheduling job: {e}")
        return jsonify({"error": str(e)}), 500

# Initialize and start the component
scheduler = BackgroundScheduler()
scheduler.add_job(encolar_tarea, 'interval', seconds=SCHEDULER_INTERVAL_SECONDS, id='encolar_tarea_job')
scheduler.start()
logging.info(f"component iniciado. respaldo zona 2 de pedidos! Encolando tareas cada {SCHEDULER_INTERVAL_SECONDS} segundos.")


if __name__ == '__main__':
    # This block is now only for local development (python main.py)
    # The scheduler is already started above.
    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
