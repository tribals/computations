from unittest.mock import Mock

from sqlalchemy.engine import Connection

from computations.models import Computation, Task
from computations.persistence import (
    ComputationsRepository,
    TasksRepository,
    table_computations,
    table_tasks,
)


def test_computations_repository_persists_computation():
    repository = ComputationsRepository()

    connection = Mock(spec=Connection)
    computation = Computation.create('SQRT', args=dict(number='+70003232357747326478176437462'))

    computation_id = repository.add(connection, computation)

    assert connection.execute.called

    args, _ = connection.execute.call_args  # TODO: waiting for 3.8

    assert args[0].compare(table_computations.insert().values(type='SQRT', args=computation.args))

    assert computation_id == connection.execute().inserted_primary_key


def test_tasks_repository_persists_task():
    repository = TasksRepository()

    connection = Mock(spec=Connection)
    computation_id = 42
    task = Task.queued(computation_id=computation_id)

    task_id = repository.add(connection, task)

    assert connection.execute.called

    args, _ = connection.execute.call_args  # TODO: waiting for 3.8

    assert args[0].compare(
        table_tasks.insert().values(status='QUEUED', computation_id=computation_id)
    )

    assert task_id == connection.execute().inserted_primary_key
