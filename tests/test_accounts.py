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
