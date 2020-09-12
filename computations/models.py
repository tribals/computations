import enum


class Computation(object):
    def __init__(self, type_, args):
        self._type = type_
        self._args = args

    @classmethod
    def create(Cls, type_, args):
        type_ = ComputationTypes(type_)

        return Cls(type_, args)


class ComputationTypes(enum.Enum):
    SQRT = 'SQRT'
