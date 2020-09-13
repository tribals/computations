import falcon
from sqlalchemy.engine import create_engine

from computations.configuration import EnvConfig
from computations.http import schemas
from computations.http.validation import jsonschema_validate
from computations.persistence import ComputationsRepository
from computations.services import ComputationsService


def create_api():
    config = EnvConfig()

    engine = create_engine(config.DATABASE_URI)
    computations_repository = ComputationsRepository()

    computations_service = ComputationsService(engine, computations_repository)

    api = falcon.API()
    api.add_route('/api/v1/computations', ComputationsResource(computations_service))
    api.add_route(
        '/api/v1/computations/{computation_id:int}', ComputationResource(computations_service)
    )
    api.add_route('/api/v1/tasks/{task_id:int}', TaskResource(computations_service))

    return api


class ComputationsResource(object):
    def __init__(self, service):
        self._service = service

    @jsonschema_validate(schemas.post_v1_computations_request)
    def on_post(self, req, resp):
        computation = req.media['computation']

        queued_task_id = self._service.enqueue_computation(
            type_=computation['type'], args=computation['args']
        )

        resp.status = falcon.HTTP_ACCEPTED
        resp.location = f'/api/v1/tasks/{queued_task_id}'  # TODO: reverse URI


class ComputationResource(object):
    def __init__(self, service):
        self._service = service

    def on_get(self, req, resp, computation_id):
        computation = self._service.get_computation_by_id(computation_id)
        resp.media = dict(
            computation=dict(
                id=computation.id,
                type=computation.type_.name,
                created_at=_serialize_dt(computation.created_at),
                computed_at=_serialize_dt(computation.computed_at),
                args=computation.args,
                result=computation.result,
                task=_serialize_task(computation.task),
            )
        )


class TaskResource(object):
    def __init__(self, service):
        self._service = service

    def on_get(self, req, resp, task_id):
        computation = self._service.get_computation_by_task_id(task_id)

        if computation.task.is_completed():
            resp.status = falcon.HTTP_SEE_OTHER
            resp.location = f'/api/v1/computations/{computation.id}'
        else:
            resp.media = dict(task=_serialize_task(computation.task))


def _serialize_task(task):
    return dict(
        id=task.id,
        status=task.status.name,
        queued_at=_serialize_dt(task.queued_at),
        started_at=_serialize_dt(task.started_at),
        completed_at=_serialize_dt(task.completed_at),
    )


def _serialize_dt(dt):
    if dt is None:
        return dt

    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
