from computations.configuration import EnvConfig


def test_env_config():
    config = EnvConfig()

    assert config.DATABASE_URI
