from unittest.mock import MagicMock, Mock, call

from sqlalchemy.engine import Connection, Engine

from computations.models import Computation
from computations.persistence import ComputationsRepository
from computations.services import ComputationsService


# NOTE: `mocker` used only for patching in order to avoid deeply-nested `with` statements
def test_computations_service_queues_computation(mocker):
    engine = Mock(spec=Engine)
    engine.begin.return_value = MagicMock(spec=Connection)
    computations_repository = Mock(spec=ComputationsRepository)

    service = ComputationsService(engine, computations_repository)

    type_ = 'SQRT'
    args = dict(number='+70003232357747326478176437462')

    ComputationMock = mocker.patch('computations.services.Computation', spec=Computation)
    celery_mock = mocker.patch('computations.services.celery')

    queued_task_id = service.enqueue_computation(type_=type_, args=args)

    assert ComputationMock.create.called
    assert ComputationMock.create.call_args == call(type_, args)

    assert engine.begin.called
    assert engine.begin().__enter__.called

    connection = engine.begin().__enter__()

    assert computations_repository.add.called
    assert computations_repository.add.call_args == call(connection, ComputationMock.create())

    assert celery_mock.current_app.send_task.called
    assert celery_mock.current_app.send_task.call_args == call(
        'computations.worker.perform_task', (ComputationMock.create().task.id,)
    )

    assert queued_task_id == ComputationMock.create().task.id


def test_computations_service_actually_performs_computation():
    engine = Mock(spec=Engine)
    engine.begin.return_value = MagicMock(spec=Connection)
    engine.connect.return_value = MagicMock(spec=Connection)
    computations_repository = Mock(spec=ComputationsRepository)
    computations_repository.query_by_task_id.return_value = Mock(spec=Computation)

    service = ComputationsService(engine, computations_repository)

    task_id = 42

    service.compute_by_task_id(task_id)

    assert engine.connect.called
    assert engine.connect().__enter__.called

    connection = engine.connect().__enter__()

    assert computations_repository.query_by_task_id.called
    assert computations_repository.query_by_task_id.call_args == call(connection, task_id)

    computation = computations_repository.query_by_task_id()

    assert computation.task_started.called
    assert computation.compute.called

    assert engine.begin.called
    assert engine.begin.call_count == 2
    assert engine.begin().__enter__.called
    assert engine.begin().__enter__.call_count == 2

    connection1 = engine.begin().__enter__()

    assert computations_repository.persist.called
    assert computations_repository.persist.call_args_list == [
        call(connection1, computation),
        call(connection1, computation),
    ]


def test_computations_service_gets_computation_by_task_id():
    engine = Mock(spec=Engine)
    engine.connect.return_value = MagicMock(spec=Connection)
    computations_repository = Mock(spec=ComputationsRepository)

    service = ComputationsService(engine, computations_repository)

    task_id = 42

    computation = service.get_computation_by_task_id(task_id)

    assert engine.connect.called
    assert engine.connect().__enter__.called

    connection = engine.connect().__enter__()

    assert computations_repository.query_by_task_id.called
    assert computations_repository.query_by_task_id.call_args == call(connection, task_id)

    assert computation == computations_repository.query_by_task_id()
