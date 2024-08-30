from celery import Celery
from config.config import config

app = Celery('docurefine',
             broker=config.CELERY_BROKER_URL,
             backend=config.CELERY_RESULT_BACKEND,
             include=['src.celery_tasks'])

app.conf.update(
    result_expires=3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

if __name__ == '__main__':
    app.start()