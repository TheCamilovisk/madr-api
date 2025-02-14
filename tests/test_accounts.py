from http import HTTPStatus


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


def test_create_account_username_exists_error(client, account):
    response = client.post(
        '/accounts/',
        json={
            'username': account.username,
            'email': 'test@test.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username or email already exists'}


def test_create_account_email_exists_error(client, account):
    response = client.post(
        '/accounts/',
        json={
            'username': 'test',
            'email': account.email,
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username or email already exists'}


def test_update_account_ok(client, account):
    response = client.put(
        f'/accounts/{account.id}',
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


def test_delete_account_ok(client, account):
    response = client.delete(f'/accounts/{account.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Account deleted'}
