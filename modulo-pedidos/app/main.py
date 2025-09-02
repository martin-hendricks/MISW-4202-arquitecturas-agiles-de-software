from flask import Flask, jsonify
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import redis
from rq import Queue
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Redis and RQ setup
redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_conn = redis.Redis(host=redis_host, port=redis_port)
q = Queue(connection=redis_conn)

# Scheduler interval configuration
SCHEDULER_INTERVAL_SECONDS = int(os.environ.get('SCHEDULER_INTERVAL_SECONDS', 5))

def encolar_tarea():
    """
    lo encola en Redis.
    """
    with app.app_context():
        pedido_id = str(uuid.uuid4())
        colombia_tz = ZoneInfo("America/Bogota")
        now_colombia = datetime.now(colombia_tz)
        timestamp = now_colombia.isoformat()

        task_payload = {
            "id": pedido_id,
            "timestamp": timestamp,
            "servicio_origen": "modulo-pedidos-1"
        }

        q.enqueue('tasks.heartbeat_ping', task_payload)
        
        print(f"Tarea encolada: {task_payload}")

@app.route('/')
def home():
    return jsonify({"mensaje": "Hola, soy el microservicio de pedidos! Ahora funciono como un scheduler."})

if __name__ == '__main__':

    scheduler = BackgroundScheduler()
    scheduler.add_job(encolar_tarea, 'interval', seconds=SCHEDULER_INTERVAL_SECONDS)
    scheduler.start()
    print(f"Scheduler iniciado. Encolando tareas cada {SCHEDULER_INTERVAL_SECONDS} segundos.")

    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()