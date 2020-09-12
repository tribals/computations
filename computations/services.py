from computations.models import Computation


class ComputationsService(object):
    def __init__(self, engine, computations_repository, tasks_scheduler):
        self._engine = engine
        self._computations_repository = computations_repository
        self._tasks_scheduler = tasks_scheduler

    def enqueue_computation(self, *, type_, args):
        computation = Computation.create(type_, args)

        with self._engine.begin() as conn:
            computation_id = self._computations_repository.add(conn, computation)
            task_id = self._tasks_scheduler.enqueue(conn, computation_id)

        return task_id
