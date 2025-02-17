from http import HTTPStatus


def test_crate_author_ok(client, token):
    response = client.post(
        '/authors',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Clarice Lispector'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'name': 'clarice lispector'}


def test_create_author_not_login_error(client):
    response = client.post(
        '/authors',
        json={'name': 'Clarice Lispector'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_create_author_name_exists_error(client, token, author):
    response = client.post(
        '/authors',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': author.name},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Author name already exists'}


def test_delete_author_ok(client, token, author):
    response = client.delete(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author deleted'}


def test_delete_author_not_logged_error(client, author):
    response = client.delete(f'/authors/{author.id}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_delete_author_not_found_error(client, token):
    response = client.delete(
        '/authors/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_update_author_ok(client, token, author):
    response = client.patch(
        f'/authors/{author.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Clarice Lispector'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': author.id, 'name': 'clarice lispector'}


def test_update_author_not_logged_error(client, author):
    response = client.patch(
        f'/authors/{author.id}',
        json={'name': 'Clarice Lispector'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_author_name_exists_error(
    client, token, author, another_author
):
    response = client.patch(
        f'/authors/{author.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': another_author.name},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Author name already exists'}


def test_update_author_not_found_error(client, token):
    response = client.patch(
        '/authors/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test name'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_read_author_detail_ok(client, author):
    response = client.get(f'/authors/{author.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': author.id, 'name': author.name}


def test_read_author_detail_author_not_found_error(client):
    response = client.get('/authors/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_read_authors_ok(client, author, another_author, one_more_author):
    response = client.get('/authors')

    expected_response = {
        'authors': [
            {'id': a.id, 'name': a.name}
            for a in (author, another_author, one_more_author)
        ]
    }

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_response


def test_read_authors_search_fullname_ok(
    client, author, another_author, one_more_author
):
    response = client.get(f'/authors?name={author.name}')

    expected_response = {'authors': [{'id': author.id, 'name': author.name}]}

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_response


def test_read_authors_search_partial_name_ok(
    client, author, another_author, one_more_author
):
    response = client.get('/authors?name=author')

    expected_response = {
        'authors': [
            {'id': a.id, 'name': a.name} for a in (author, another_author)
        ]
    }

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_response


def test_read_authors_without_authors_ok(client):
    response = client.get('/authors')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'authors': []}
