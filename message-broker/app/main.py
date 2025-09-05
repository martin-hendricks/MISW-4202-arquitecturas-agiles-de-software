import os
import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))

if __name__ == '__main__':
    redis_conn = redis.Redis(host=redis_host, port=redis_port)
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
