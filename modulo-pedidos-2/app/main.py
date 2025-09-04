from flask import Flask, jsonify
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
SCHEDULER_INTERVAL_SECONDS = int(os.environ.get('SCHEDULER_INTERVAL_SECONDS', 9))

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
            "servicio_origen": "modulo-pedidos-2"
        }

        q.enqueue('tasks.heartbeat_ping', task_payload)
        
        logging.info(f"Tarea encolada: {task_payload}")

@app.route('/')
def home():
    return jsonify({"mensaje": "Hola, soy el microservicio de respaldo zona 1 de pedidos! Ahora funciono como un scheduler."})

# Initialize and start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(encolar_tarea, 'interval', seconds=SCHEDULER_INTERVAL_SECONDS)
scheduler.start()
logging.info(f"Scheduler iniciado. respaldo zona 1 de pedidos! Encolando tareas cada {SCHEDULER_INTERVAL_SECONDS} segundos.")


if __name__ == '__main__':
    # This block is now only for local development (python main.py)
    # The scheduler is already started above.
    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()