from computations.models import Computation, TaskStatuses


def test_computation_create_factory_creates_it_in_consistent_state():
    type_ = 'SQRT'
    args = dict(number='+70003232357747326478176437462')

    computation = Computation.create(type_=type_, args=args)

    assert computation.task.status == TaskStatuses.QUEUED
