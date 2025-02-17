from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from madr_api.database import get_session
from madr_api.models import Author, Book, UserAccount
from madr_api.schemas import (
    BookList,
    BookPublic,
    BookSchema,
    BooksFilterPage,
    BookUpdate,
    Message,
)
from madr_api.security import get_current_user_account
from madr_api.utils import sanitize_string

router = APIRouter(prefix='/books', tags=['books'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=BookPublic)
def create_book(
    new_book: BookSchema,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    new_title = sanitize_string(new_book.title)
    db_book = Book(
        title=new_title, year=new_book.year, author_id=new_book.author_id
    )

    try:
        session.add(db_book)
        session.commit()
        session.refresh(db_book)

        return db_book
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Book title already exists',
        )


@router.delete('/{book_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_book(
    book_id: int,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    db_book = session.scalar(select(Book).where(Book.id == book_id))
    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    session.delete(db_book)
    session.commit()

    return {'message': 'Book deleted'}


@router.patch(
    '/{book_id}', status_code=HTTPStatus.OK, response_model=BookPublic
)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    db_book = session.scalar(select(Book).where(Book.id == book_id))
    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    try:
        for key, value in book_data.model_dump(exclude_unset=True).items():
            if key == 'author_id':
                db_author = session.scalar(
                    select(Author).where(Author.id == value)
                )
                if not db_author:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail='Author not found',
                    )
            setattr(db_book, key, value)

        session.add(db_book)
        session.commit()
        session.refresh(db_book)

        return db_book
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Book title already exists'
        )


@router.get('/', status_code=HTTPStatus.OK, response_model=BookList)
def fetch_books(
    filter_page: BooksFilterPage = Depends(),
    session: Session = Depends(get_session),
):
    query = select(Book)

    if title := filter_page.title:
        query = query.where(Book.title.contains(title))

    if year := filter_page.year:
        query = query.where(Book.year == year)

    query = query.offset(filter_page.offset).limit(filter_page.limit)

    books = session.scalars(query).all()

    return {'books': books}


@router.get('/{book_id}', status_code=HTTPStatus.OK, response_model=BookPublic)
def read_book_details(book_id: int, session: Session = Depends(get_session)):
    db_book = session.scalar(select(Book).where(Book.id == book_id))
    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    return db_book
