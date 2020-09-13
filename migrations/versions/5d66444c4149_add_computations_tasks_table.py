"""add computations, tasks table

Revision ID: 5d66444c4149
Revises: 
Create Date: 2020-09-13 19:38:04.581559

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5d66444c4149'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'computations',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('computed_at', sa.DateTime()),
        sa.Column(
            'type',
            sa.Enum('SQRT', create_constraint=True, name='computationtypes', native_enum=False),
            nullable=False,
        ),
        sa.Column('args', postgresql.JSONB(), server_default='{}'),
        sa.Column('result', postgresql.JSONB(), server_default='{}'),
    )
    op.create_table(
        'tasks',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('queued_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column(
            'status',
            sa.Enum(
                'QUEUED',
                'STARTED',
                'COMPLETED',
                create_constraint=True,
                name='taskstatuses',
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            'computation_id', sa.BigInteger(), sa.ForeignKey('computations.id'), nullable=False
        ),
    )


def downgrade():
    op.drop_table('tasks')
    op.drop_table('computations')
