from http import HTTPStatus


def test_get_token(client, account):
    response = client.post(
        '/auth/token',
        data={'username': account.email, 'password': account.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
