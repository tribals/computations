# from sqlalchemy.engine import create_engine
from contextlib import contextmanager

import falcon

# from computations.configuration import EnvConfig
from computations.http import schemas
from computations.http.validation import jsonschema_validate
from computations.persistence import ComputationsRepository, TasksRepository
from computations.services import ComputationsService
from computations.worker import TasksScheduler


class Dummy:
    @contextmanager
    def begin(self):
        yield


def create_api():
    # config = EnvConfig()

    # engine = create_engine(config.DATABASE_URI)
    computations_repository = ComputationsRepository()
    tasks_repository = TasksRepository()

    tasks_scheduler = TasksScheduler(tasks_repository)

    computations_service = ComputationsService(Dummy(), computations_repository, tasks_scheduler)

    api = falcon.API()
    api.add_route('/api/v1/computations', ComputationsResource(computations_service))

    return api


class ComputationsResource(object):
    def __init__(self, service):
        self._service = service

    @jsonschema_validate(schemas.v1_post_computations_request)
    def on_post(self, req, resp):
        computation = req.media['computation']

        queued_task_id = self._service.enqueue_computation(
            type_=computation['type'], args=computation['args']
        )

        resp.status = falcon.HTTP_ACCEPTED
        resp.location = f'/api/v1/tasks/{queued_task_id}'  # TODO: reverse URI
