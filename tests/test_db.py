from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_api.database import engine, get_session
from madr_api.models import UserAccount


def test_create_user_account(session, mock_db_time):
    with mock_db_time(model=UserAccount) as time:
        new_account = UserAccount(
            username='fausto', email='fausto@fausto.com', password='secret'
        )

        session.add(new_account)
        session.commit()

    account = session.scalar(
        select(UserAccount).where(UserAccount.username == 'fausto')
    )

    assert asdict(account) == {
        'id': 1,
        'username': 'fausto',
        'email': 'fausto@fausto.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }


def test_get_session():
    session = next(get_session())

    assert isinstance(session, Session)
    assert session.bind == engine
