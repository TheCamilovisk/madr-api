from http import HTTPStatus

from sqlalchemy import select

from madr_api.models import UserAccount


# Testa se o endopoint the lita de consta retorna OK
def test_read_users_ok(client, account):
    response = client.get('/accounts/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'accounts': [
            {
                'id': account.id,
                'username': account.username,
                'email': account.email,
            }
        ]
    }


# Testa se o endpoint de criação de contas retorna OK
def test_create_account_ok(client):
    response = client.post(
        '/accounts/',
        json={
            'username': 'fausto',
            'email': 'fausto@fausto.com',
            'password': '1234567',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'fausto',
        'email': 'fausto@fausto.com',
    }


# Testa se o endpoint de criação de conta retorna erro se já houver o nome de
# usuário já existe.
def test_create_account_username_exists_error(client, account):
    response = client.post(
        '/accounts/',
        json={
            'username': account.username,
            'email': 'test@test.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


# Testa se o endpoint de criação de conta retorna erro se já houver o email já
# existe.
def test_create_account_email_exists_error(client, account):
    response = client.post(
        '/accounts/',
        json={
            'username': 'test',
            'email': account.email,
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


# Testa se o endpoint de atualização de conta retorna erro se já houver o
# usuário não estiver logado.
def test_update_account_not_logged_error(client, account):
    response = client.put(
        f'/accounts/{account.id}',
        json={
            'username': 'other_username',
            'email': 'other_mail@fausto.com',
            'password': 'other_password',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


# Testa se o endpoint de atualização de conta retorna erro se já houver o
# usuário a ser atualizanão não for o mesmo que está logado.
def test_update_account_wrong_account_error(client, another_account, token):
    response = client.put(
        f'/accounts/{another_account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'other_username',
            'email': 'other_mail@fausto.com',
            'password': 'other_password',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


# Testa se o endpoint de atualização de conta retorna OK.
def test_update_account_ok(client, account, token, session):
    response = client.put(
        f'/accounts/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'other_username',
            'email': 'other_mail@fausto.com',
            'password': 'other_password',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': account.id,
        'username': 'other_username',
        'email': 'other_mail@fausto.com',
    }

    db_account = session.scalar(
        select(UserAccount).where(UserAccount.id == account.id)
    )

    assert db_account.username == account.username
    assert db_account.email == account.email


# Testa se o endpoint de atualização de conta retorna erro se já houver uma
# conta com o nome de usuário.
def test_update_account_username_already_exists_error(
    client, account, another_account, token
):
    response = client.put(
        f'/accounts/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': another_account.username,
            'email': 'test@test.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


# Testa se o endpoint de atualização de conta retorna erro se já houver uma
# conta com o email.
def test_update_account_email_already_exists_error(
    client, account, another_account, token
):
    response = client.put(
        f'/accounts/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test',
            'email': another_account.email,
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


# Testa se o endpoint de deleção de conta retorna OK.
def test_delete_account_ok(client, account, token):
    response = client.delete(
        f'/accounts/{account.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Account deleted'}


# Testa se o endpoint de deleção de conta retorna erro se usuário não estiver
# logado.
def test_delete_account_not_logged_error(client, another_account):
    response = client.delete(
        f'/accounts/{another_account.id}',
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


# Testa se o endpoint de deleção de conta retorna erro se a conta não for a
# mesma do usuário logado.
def test_delete_account_wrong_account_error(client, another_account, token):
    response = client.delete(
        f'/accounts/{another_account.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
