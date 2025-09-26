from flask import Flask, jsonify, request
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import redis
from rq import Queue
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import random

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

PAISES = ['CO','MX','PE','VE','BR', 'AR', 'CL', 'UY']

def encolar_tarea():
    """
    Encola una tarea en Redis.
    """
    with app.app_context():
        pedido_id = str(uuid.uuid4())
        colombia_tz = ZoneInfo("America/Bogota")
        now_colombia = datetime.now(colombia_tz)
        timestamp = now_colombia.isoformat()
        id_usuario = random.randint(1, 20)
        pais_consulta = random.choice(PAISES)

        task_payload = {
            "id": pedido_id,
            "timestamp": timestamp,
            "id_usuario": id_usuario,
            "pais_consulta": pais_consulta
        }

        q.enqueue('tasks.evento_ping', task_payload)
        
        logging.info(f"Tarea encolada: {task_payload}")



# Initialize and start the component
scheduler = BackgroundScheduler()
scheduler.add_job(encolar_tarea, 'interval', seconds=SCHEDULER_INTERVAL_SECONDS, id='encolar_tarea_job')
scheduler.start()
logging.info(f"component iniciado. Encolando tareas cada {SCHEDULER_INTERVAL_SECONDS} segundos.")


if __name__ == '__main__':
    # This block is now only for local development (python main.py)
    # The scheduler is already started above.
    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
