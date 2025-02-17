from http import HTTPStatus

from tests.conftest import BookFactory


def test_create_book_ok(client, token, author):
    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Café Da Manhã Dos Campeões',
            'year': 1973,
            'author_id': author.id,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'café da manhã dos campeões',
        'year': 1973,
        'author_id': author.id,
    }


def test_create_book_not_logged_error(client, author):
    response = client.post(
        '/books',
        json={
            'title': 'Café Da Manhã Dos Campeões',
            'year': 1973,
            'author_id': author.id,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Not authenticated',
    }


def test_create_book_title_already_exists(session, client, token, author):
    test_book = BookFactory(title='test title', author_id=author.id)

    session.add(test_book)
    session.commit()

    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': test_book.title,
            'year': test_book.year,
            'author_id': test_book.author_id,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book title already exists'}


def test_create_book_author_not_found_error(session, client, token):
    test_book = BookFactory(title='test title', author_id=1)

    session.add(test_book)
    session.commit()

    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': test_book.title,
            'year': test_book.year,
            'author_id': test_book.author_id,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Author not found'}


def test_delete_book_ok(client, token, book):
    response = client.delete(
        f'/books/{book.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book deleted'}


def test_delete_book_not_logged_error(client, book):
    response = client.delete(f'/books/{book.id}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_delete_book_not_found_error(client, token):
    response = client.delete(
        '/books/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_update_book_update_title_ok(client, token, book):
    new_title = 'Modified title'
    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': new_title},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': new_title,
        'year': book.year,
        'author_id': book.author_id,
    }


def test_update_book_update_title_already_exists_error(
    client, token, book, another_book
):
    new_title = another_book.title
    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': new_title},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book title already exists'}


def test_update_book_update_year_ok(client, token, book):
    new_year = 2000
    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'year': new_year},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': book.title,
        'year': new_year,
        'author_id': book.author_id,
    }


def test_update_book_update_author_ok(client, token, another_author, book):
    new_author = another_author.id
    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'author_id': new_author},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': book.title,
        'year': book.year,
        'author_id': new_author,
    }


def test_update_book_update_author_not_found_error(client, token, book):
    new_author = 42
    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'author_id': new_author},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Author not found'}


def test_update_book_update_not_logged_error(client, book):
    new_author = 42
    response = client.patch(
        f'/books/{book.id}',
        json={'author_id': new_author},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_book_update_book_not_found_error(client, token):
    new_title = 'Test title'
    response = client.patch(
        '/books/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': new_title},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_read_book_details_ok(client, book):
    response = client.get(f'/books/{book.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': book.title,
        'year': book.year,
        'author_id': book.author_id,
    }


def test_read_book_details_not_found_error(client):
    response = client.get('/books/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_fetch_books_by_title_ok(client, session, author, another_author):
    books_1 = BookFactory.create_batch(2, author_id=author.id)
    books_2 = BookFactory.create_batch(2, author_id=another_author.id)
    special_book_1 = BookFactory(title='Special 1', author_id=author.id)
    special_book_2 = BookFactory(
        title='Special 2', author_id=another_author.id
    )

    books = books_1 + books_2 + [special_book_1, special_book_2]

    session.bulk_save_objects(books)
    session.commit()

    expected_books = len(books_1) + len(books_2)

    response = client.get('/books/?title=title')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


def test_fetch_books_by_year_ok(client, session, author, another_author):
    books_1 = BookFactory.create_batch(2, author_id=author.id, year=2010)
    books_2 = BookFactory.create_batch(
        2, author_id=another_author.id, year=2013
    )
    books_3 = BookFactory.create_batch(2, author_id=author.id, year=2013)
    books_4 = BookFactory.create_batch(
        2, author_id=another_author.id, year=2015
    )

    books = books_1 + books_2 + books_3 + books_4

    session.bulk_save_objects(books)
    session.commit()

    expected_books = len(books_2) + len(books_3)

    response = client.get('/books/?year=2013')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


def test_fetch_books_by_title_and_year_ok(
    client, session, author, another_author
):
    book_1 = BookFactory(author_id=author.id, year=2010)
    book_2 = BookFactory(author_id=another_author.id, year=2010)
    special_book_1 = BookFactory(
        title='special 1', author_id=author.id, year=2013
    )
    special_book_2 = BookFactory(
        title='special 2', author_id=another_author.id, year=2013
    )
    special_book_3 = BookFactory(
        title='special 3', author_id=another_author.id, year=2013
    )
    book_3 = BookFactory(author_id=author.id, year=2013)
    book_4 = BookFactory(author_id=another_author.id, year=2015)

    books = [
        book_1,
        book_2,
        special_book_1,
        special_book_2,
        special_book_3,
        book_3,
        book_4,
    ]

    session.bulk_save_objects(books)
    session.commit()

    expected_books = 3

    response = client.get('/books/?title=special&year=2013')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


def test_fetch_books_empty_ok(client, session, author, another_author):
    books = BookFactory.create_batch(
        2, author_id=author.id, year=2010
    ) + BookFactory.create_batch(2, author_id=another_author.id, year=2010)

    session.bulk_save_objects(books)
    session.commit()

    response = client.get('/books/?title=special&year=2013')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'books': []}
