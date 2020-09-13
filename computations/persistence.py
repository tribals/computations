from datetime import datetime

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import Column, ForeignKey, MetaData, Table
from sqlalchemy.sql import select
from sqlalchemy.types import BigInteger, DateTime, Enum

from computations.models import Computation, Task

metadata = MetaData()

table_computations = Table(
    'computations',
    metadata,
    Column('id', BigInteger, primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('computed_at', DateTime),
    Column(
        'type',
        Enum('SQRT', create_constraint=True, name='computationtypes', native_enum=False),
        nullable=False,
    ),
    Column('args', postgresql.JSONB, default=dict),
    Column('result', postgresql.JSONB, default=dict),
)

table_tasks = Table(
    'tasks',
    metadata,
    Column('id', BigInteger, primary_key=True),
    Column('queued_at', DateTime, default=datetime.utcnow),
    Column('started_at', DateTime),
    Column('completed_at', DateTime),
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

        computation.id = result.inserted_primary_key[0]  # TODO

        result = connection.execute(
            table_tasks.insert().values(
                status=computation.task.status.name, computation_id=computation.id
            )
        )

        computation.task.id = result.inserted_primary_key[0]  # TODO

    def query_by_task_id(self, connection, task_id):
        result = connection.execute(
            select([table_computations, table_tasks])
            .select_from(table_computations.join(table_tasks))
            .where(table_tasks.c.id == task_id)
        )

        return _deserialize(result.one())

    def query_by_id(self, connection, computation_id):
        result = connection.execute(
            select([table_computations, table_tasks])
            .select_from(table_computations.join(table_tasks))
            .where(table_computations.c.id == computation_id)
        )

        return _deserialize(result.one())

    def persist(self, connection, computation):
        connection.execute(
            table_tasks.update()
            .values(
                status=computation.task.status.name,
                started_at=computation.task.started_at,
                completed_at=computation.task.completed_at,
            )
            .where(table_tasks.c.id == computation.task.id)
        )
        connection.execute(
            table_computations.update()
            .values(
                result=computation.result,
                computed_at=computation.computed_at,
            )
            .where(table_computations.c.id == computation.id)
        )


def _deserialize(row):
    return Computation.reconstitute(
        row[table_computations.c.type],
        row[table_computations.c.args],
        Task.reconstitute(
            row[table_tasks.c.status],
            row[table_tasks.c.id],
            row[table_tasks.c.queued_at],
            row[table_tasks.c.started_at],
            row[table_tasks.c.completed_at],
        ),
        row[table_computations.c.id],
        row[table_computations.c.result],
        row[table_computations.c.created_at],
        row[table_computations.c.computed_at],
    )
