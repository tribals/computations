import enum


class Computation(object):
    def __init__(
        self, type_, args, task, id_=None, result=None, created_at=None, computed_at=None
    ):
        self._type = type_
        self._args = args
        self._task = task
        self._id = id_
        self._result = result
        self._created_at = created_at
        self._computed_at = computed_at

    def task_started(self):
        pass

    def compute(self):
        pass

    @property
    def type_(self):
        return self._type

    @property
    def args(self):
        return self._args

    @property
    def task(self):
        return self._task

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def result(self):
        return self._result

    @property
    def created_at(self):
        return self._created_at

    @property
    def computed_at(self):
        return self._computed_at

    @classmethod
    def create(Cls, type_, args):
        return Cls(ComputationTypes(type_), args, Task.queued())

    @classmethod
    def reconstitute(Cls, type_, args, task, id_, result, created_at, computed_at):
        return Cls(ComputationTypes(type_), args, task, id_, result, created_at, computed_at)


class ComputationTypes(enum.Enum):
    SQRT = 'SQRT'


class Task(object):
    def __init__(self, status, id_=None, queued_at=None, started_at=None, completed_at=None):
        self._status = status
        self._id = id_
        self._queued_at = queued_at
        self._started_at = started_at
        self._completed_at = completed_at

    @property
    def status(self):
        return self._status

    def is_completed(self):
        return self._status is TaskStatuses.COMPLETED

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def queued_at(self):
        return self._queued_at

    @property
    def started_at(self):
        return self._started_at

    @property
    def completed_at(self):
        return self._completed_at

    @classmethod
    def queued(Cls):
        return Cls(TaskStatuses.QUEUED)

    @classmethod
    def reconstitute(Cls, status, id_, queued_at, started_at, completed_at):
        return Cls(TaskStatuses(status), id_, queued_at, started_at, completed_at)


class TaskStatuses(enum.Enum):
    QUEUED = 'QUEUED'
    STARTED = 'STARTED'
    COMPLETED = 'COMPLETED'
