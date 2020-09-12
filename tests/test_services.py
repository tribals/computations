from unittest.mock import MagicMock, Mock, call, patch

from sqlalchemy.engine import Connection, Engine

from computations.models import Computation
from computations.persistence import ComputationsRepository
from computations.services import ComputationsService
from computations.worker import TasksScheduler


def test_computations_service_queues_computation():
    engine = Mock(spec=Engine)
    engine.begin.return_value = MagicMock(spec=Connection)
    computations_repository = Mock(spec=ComputationsRepository)
    tasks_scheduler = Mock(spec=TasksScheduler)

    service = ComputationsService(engine, computations_repository, tasks_scheduler)

    type_ = 'SQRT'
    args = dict(number='+70003232357747326478176437462')

    with patch('computations.services.Computation', spec=Computation) as ComputationMock:
        queued_task_id = service.enqueue_computation(type_=type_, args=args)

    assert ComputationMock.create.called
    assert ComputationMock.create.call_args == call(type_, args)

    assert queued_task_id == tasks_scheduler.enqueue.return_value

    assert engine.begin.called
    assert engine.begin().__enter__.called

    connection = engine.begin().__enter__()

    assert computations_repository.add.called
    assert computations_repository.add.call_args == call(connection, ComputationMock.create())

    assert tasks_scheduler.enqueue.called
    assert tasks_scheduler.enqueue.call_args == call(connection, computations_repository.add())
