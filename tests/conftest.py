import pytest
from sqlalchemy.engine import create_engine

from computations.configuration import EnvConfig


@pytest.fixture(scope='session')
def config():
    return EnvConfig()


@pytest.fixture(scope='session')
def engine(config):
    return create_engine(config.DATABASE_URI)


@pytest.fixture
def transactional_connection(engine):
    # SEE: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    with engine.connect() as conn:
        txn = conn.begin()

        yield conn

        txn.rollback()
