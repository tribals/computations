import enum


class Computation(object):
    def __init__(self, type_, args, task, id_=None, result=None):
        self._type = type_
        self._args = args
        self._task = task
        self._id = id_
        self._result = result

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

    @classmethod
    def create(Cls, type_, args):
        return Cls(ComputationTypes(type_), args, Task.queued())

    @classmethod
    def reconstitute(Cls, type_, args, task, id_, result):
        return Cls(ComputationTypes(type_), args, task, id_, result)


class ComputationTypes(enum.Enum):
    SQRT = 'SQRT'


class Task(object):
    def __init__(self, status, id_=None):
        self._status = status
        self._id = id_

    @property
    def status(self):
        return self._status

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @classmethod
    def queued(Cls):
        return Cls(TaskStatuses.QUEUED)

    @classmethod
    def reconstitute(Cls, status, id_):
        return Cls(TaskStatuses(status), id_)


class TaskStatuses(enum.Enum):
    QUEUED = 'QUEUED'
    STARTED = 'STARTED'
    COMPLETED = 'COMPLETED'
