from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session

from madr_api.app import app
from madr_api.database import get_session
from madr_api.models import UserAccount, table_registry
from madr_api.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


def bootstrap_attr(target, attr, value):
    if hasattr(target, attr):
        setattr(target, attr, value)


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        for attr in ('created_at', 'updated_at'):
            bootstrap_attr(target, attr, time)

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def account(session):
    password = 'test'
    account = UserAccount(
        username='Test',
        email='test@test.com',
        password=get_password_hash(password),
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    account.clean_password = password

    return account
