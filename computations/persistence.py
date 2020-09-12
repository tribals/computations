from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import Column, ForeignKey, MetaData, Table
from sqlalchemy.types import BigInteger, Enum

metadata = MetaData()

table_computations = Table(
    'computations',
    metadata,
    Column('id', BigInteger, primary_key=True),
    Column(
        'type',
        Enum('SQRT', create_constraint=True, name='computationtypes', native_enum=False),
        nullable=False,
    ),
    Column('args', postgresql.JSONB, default=dict),
)

table_tasks = Table(
    'tasks',
    metadata,
    Column('id', BigInteger, primary_key=True),
    Column(
        'status',
        Enum(
            'QUEUED',
            'STARTED',
            'COMPLETED',
            create_constraint=True,
            name='taskstatuses',
            native_enum=False,
        ),
        nullable=False,
    ),
    Column('computation_id', BigInteger, ForeignKey('computations.id'), nullable=False),
)


class ComputationsRepository(object):
    def add(self, connection, computation):
        result = connection.execute(
            table_computations.insert().values(type=computation.type_.name, args=computation.args)
        )

        return result.inserted_primary_key


class TasksRepository(object):
    def add(self, connection, task):
        result = connection.execute(
            table_tasks.insert().values(
                status=task.status.name, computation_id=task.computation_id
            )
        )

        return result.inserted_primary_key
