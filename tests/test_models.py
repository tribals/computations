from unittest.mock import call

from computations.models import Computation, SquareRootStrategy

_DOESNT_MATTER = object()


def test_computation_create_factory_creates_it_in_consistent_state():
    type_ = 'SQRT'
    args = dict(number='+70003232357747326478176437462')

    computation = Computation.create(type_=type_, args=args)

    assert computation.task.is_queued()


def test_computation_computes_itself(mocker):
    type_ = 'SQRT'
    args = dict(number='+70003232357747326478176437462')

    computation = Computation.create(type_=type_, args=args)

    SquareRootStrategyMock = mocker.patch(
        'computations.models.SquareRootStrategy', spec=SquareRootStrategy
    )
    datetime_mock = mocker.patch('computations.models.datetime')

    computation.compute()

    assert SquareRootStrategyMock.called
    assert SquareRootStrategyMock.call_args == call(**args)
    assert SquareRootStrategyMock().compute.called

    assert computation.result == SquareRootStrategyMock().compute()
    assert computation.computed_at == datetime_mock.utcnow()


def test_computation_task_started(mocker):
    type_ = 'SQRT'
    args = dict(number='+70003232357747326478176437462')

    computation = Computation.create(type_=type_, args=args)

    datetime_mock = mocker.patch('computations.models.datetime')

    computation.task_started()

    assert computation.task.is_started()
    assert computation.task.started_at == datetime_mock.utcnow()


def test_computation_task_completed(mocker):
    type_ = 'SQRT'
    args = dict(number='+70003232357747326478176437462')

    computation = Computation.create(type_=type_, args=args)

    datetime_mock = mocker.patch('computations.models.datetime')

    computation.task_completed()

    assert computation.task.is_completed()
    assert computation.task.completed_at == datetime_mock.utcnow()


def test_square_root_strategy(mocker):
    args = dict(number='+99999999999999409792567484569')

    strategy = SquareRootStrategy(**args)

    localcontext_mock = mocker.patch('computations.models.localcontext')
    ContextMock = mocker.patch('computations.models.Context')

    result = strategy.compute()

    assert ContextMock.called
    assert ContextMock.call_args == call(prec=1015)

    assert localcontext_mock.called
    assert localcontext_mock.call_args == call(ContextMock())
    assert localcontext_mock().__enter__.called

    assert result == dict(number='316227766016837')
