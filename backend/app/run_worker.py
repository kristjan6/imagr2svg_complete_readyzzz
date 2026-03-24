from redis import Redis
from rq import Worker, Queue

from app.config import settings

redis_conn = Redis.from_url(settings.redis_url)
queue = Queue(settings.rq_queue, connection=redis_conn)

if __name__ == "__main__":
    worker = Worker([queue], connection=redis_conn)
    worker.work()
