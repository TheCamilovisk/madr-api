from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session

from madr_api.app import app
from madr_api.database import get_session
from madr_api.models import Author, Book, UserAccount, table_registry
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


class AccountFactory(factory.Factory):
    class Meta:
        model = UserAccount

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


@pytest.fixture
def account(session):
    password = 'testtest'
    account = AccountFactory(password=get_password_hash(password))

    session.add(account)
    session.commit()
    session.refresh(account)

    account.clean_password = password

    return account


@pytest.fixture
def another_account(session):
    password = 'testtest'
    account = AccountFactory(password=get_password_hash(password))

    session.add(account)
    session.commit()
    session.refresh(account)

    account.clean_password = password

    return account


@pytest.fixture
def token(client, account):
    response = client.post(
        '/auth/token',
        data={
            'username': account.username,
            'password': account.clean_password,
        },
    )
    return response.json()['access_token']


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: f'author{n}')


@pytest.fixture
def author(session):
    author = AuthorFactory()

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


@pytest.fixture
def another_author(session):
    author = AuthorFactory()

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


@pytest.fixture
def one_more_author(session):
    author = AuthorFactory(name='special')

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f'title{n}')
    year = 1999
    author_id = 1

    # Here we're using factory.PostGeneration to set the created_at and
    # updated_at fields after the instance is created. This avoids passing them
    # as arguments to the constructor.
    # In this approach:
    #   - The set_timestamps method is a post-generation hook that sets the
    #     created_at and updated_at fields after the instance is created.
    #   - The create parameter ensures that the hook only runs when the
    #     instance is actually created (not when building or stubbing).
    @factory.post_generation
    def set_timestamps(self, create, extracted, **kwargs):
        if create:
            self.created_at = datetime.now()
            self.updated_at = datetime.now()


@pytest.fixture
def book(session, author):
    book = BookFactory(author_id=author.id)

    session.add(book)
    session.commit()

    return book


@pytest.fixture
def another_book(session, author):
    book = BookFactory(author_id=author.id)

    session.add(book)
    session.commit()

    return book
