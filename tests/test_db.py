from dataclasses import asdict

from sqlalchemy import select

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
