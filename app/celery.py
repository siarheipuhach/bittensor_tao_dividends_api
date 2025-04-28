from celery import Celery
from app.config import settings


celery_app = Celery("bittensor_worker")
celery_app.conf.broker_url = settings.redis_url
celery_app.conf.result_backend = settings.redis_url
celery_app.conf.task_routes = {"app.celery.background.*": {"queue": "default"}}

celery_app.autodiscover_tasks(["app.tasks.bittensor"])
