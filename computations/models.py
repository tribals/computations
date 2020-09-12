import enum


class Computation(object):
    def __init__(self, type_, args):
        self._type = type_
        self._args = args

    @property
    def type_(self):
        return self._type

    @property
    def args(self):
        return self._args

    @classmethod
    def create(Cls, type_, args):
        type_ = ComputationTypes(type_)

        return Cls(type_, args)


class ComputationTypes(enum.Enum):
    SQRT = 'SQRT'


class Task(object):
    def __init__(self, status, computation_id):
        self._status = status
        self._computation_id = computation_id

    @property
    def status(self):
        return self._status

    @property
    def computation_id(self):
        return self._computation_id

    @classmethod
    def queued(Cls, computation_id):
        return Cls(TaskStatuses.QUEUED, computation_id)


class TaskStatuses(enum.Enum):
    QUEUED = 'QUEUED'
    STARTED = 'STARTED'
    COMPLETED = 'COMPLETED'
