from celery import Celery
from sqlalchemy.engine import create_engine

from computations.configuration import EnvConfig
from computations.persistence import ComputationsRepository
from computations.services import ComputationsService

app = Celery('computations.worker')


@app.task
def perform_task(task_id):
    config = EnvConfig()
    engine = create_engine(config.DATABASE_URI)
    computations_repository = ComputationsRepository()

    computations_service = ComputationsService(engine, computations_repository)
    computations_service.compute_by_task_id(task_id)
