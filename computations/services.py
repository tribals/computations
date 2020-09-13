import celery

from computations.models import Computation


class ComputationsService(object):
    def __init__(self, engine, computations_repository):
        self._engine = engine
        self._computations_repository = computations_repository

    def enqueue_computation(self, *, type_, args):
        computation = Computation.create(type_, args)

        with self._engine.begin() as conn:
            self._computations_repository.add(conn, computation)

            celery.current_app.send_task(
                'computations.worker.perform_task', (computation.task.id,)
            )

        return computation.task.id

    def compute_by_task_id(self, task_id):
        with self._engine.connect() as conn:
            computation = self._computations_repository.query_by_task_id(conn, task_id)

        computation.task_started()

        with self._engine.begin() as conn:
            self._computations_repository.persist(conn, computation)

        computation.compute()

        with self._engine.begin() as conn:
            self._computations_repository.persist(conn, computation)

    def get_computation_by_task_id(self, task_id):
        with self._engine.connect() as conn:
            return self._computations_repository.query_by_task_id(conn, task_id)
