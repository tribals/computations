from unittest.mock import MagicMock, Mock, call

from sqlalchemy.engine import Connection, CursorResult, Row
from sqlalchemy.sql import select

from computations.models import Computation, Task
from computations.persistence import ComputationsRepository, table_computations, table_tasks


def test_computations_repository_add():
    repository = ComputationsRepository()

    connection = Mock(spec=Connection)
    connection.execute.return_value = MagicMock(spec=CursorResult)

    computation = Computation.create('SQRT', args=dict(number='+70003232357747326478176437462'))

    repository.add(connection, computation)

    assert connection.execute.called
    assert connection.execute.call_count == 2

    # SEE: https://docs.python.org/3/library/unittest.mock.html#calls-as-tuples
    (first_call_args, _), (second_call_args, _) = connection.execute.call_args_list

    assert first_call_args[0].compare(
        table_computations.insert().values(type='SQRT', args=computation.args)
    )
    assert second_call_args[0].compare(
        table_tasks.insert().values(
            status='QUEUED', computation_id=connection.execute().inserted_primary_key[0]
        )
    )


def test_computations_repository_query_by_task_id(mocker):
    repository = ComputationsRepository()

    connection = Mock(spec=Connection)
    connection.execute.return_value.first.return_value = MagicMock(spec=Row)

    task_id = 42

    ComputationMock = mocker.patch('computations.persistence.Computation', spec=Computation)
    TaskMock = mocker.patch('computations.persistence.Task', spec=Task)

    repository.query_by_task_id(connection, task_id)

    assert connection.execute.called

    args, _ = connection.execute.call_args  # TODO: waiting for 3.8

    assert args[0].compare(
        select([table_computations, table_tasks])
        .select_from(table_computations.join(table_tasks))
        .where(table_tasks.c.id == task_id)
    )
    assert connection.execute().first.called

    row = connection.execute().first()

    assert TaskMock.reconstitute.called
    assert TaskMock.reconstitute.call_args == call(
        row[table_tasks.c.status], row[table_tasks.c.id]
    )

    assert ComputationMock.reconstitute.called
    assert ComputationMock.reconstitute.call_args == call(
        row[table_computations.c.type],
        row[table_computations.c.args],
        TaskMock.reconstitute(),
        row[table_computations.c.id],
        row[table_computations.c.result],
    )


def test_computations_repository_persist():
    repository = ComputationsRepository()

    connection = Mock(spec=Connection)

    computation = Computation.create('SQRT', args=dict(number='+70003232357747326478176437462'))
    computation.id = 42
    computation.task.id = 420

    repository.persist(connection, computation)

    assert connection.execute.called
    assert connection.execute.call_count == 2

    # SEE: https://docs.python.org/3/library/unittest.mock.html#calls-as-tuples
    (first_call_args, _), (second_call_args, _) = connection.execute.call_args_list

    assert first_call_args[0].compare(
        table_tasks.update()
        .values(status=computation.task.status)
        .where(table_tasks.c.id == computation.task.id)
    )
    assert second_call_args[0].compare(
        table_computations.update()
        .values(result=computation.result)
        .where(table_computations.c.id == computation.id)
    )
