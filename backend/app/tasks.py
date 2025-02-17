from celery import Celery
from app.algo.maintenance.maintenance import core_maintenance

celery = Celery(__name__)

@celery.task
def async_k_eta_core(k, eta):
    return core_maintenance(k, eta)