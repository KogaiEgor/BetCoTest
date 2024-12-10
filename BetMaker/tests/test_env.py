def test_environment_variables():
    import os
    assert os.getenv("DATABASE_URL") == "postgresql+asyncpg://postgres:postgres@db:5432/bet_maker_test"
    assert os.getenv("RABBITMQ_URL") == "amqp://guest:guest@rabbitmq/"