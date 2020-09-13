from unittest.mock import call

from computations.worker import perform_task


def test_perform_task_delegates_to_service(mocker):
    task_id = 42

    ComputationsServiceMock = mocker.patch('computations.worker.ComputationsService')

    perform_task(task_id)

    assert ComputationsServiceMock.called
    assert ComputationsServiceMock().compute_by_task_id.called
    assert ComputationsServiceMock().compute_by_task_id.call_args == call(task_id)
