from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from madr_api.database import get_session
from madr_api.models import Author, UserAccount
from madr_api.schemas import (
    AuthorList,
    AuthorPublic,
    AuthorSchema,
    AuthorsFilterPage,
    Message,
)
from madr_api.security import get_current_user_account
from madr_api.utils import sanitize_string

router = APIRouter(prefix='/authors', tags=['authors'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AuthorPublic)
def create_author(
    new_author: AuthorSchema,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    author_name = sanitize_string(new_author.name)

    try:
        db_author = Author(name=author_name)
        session.add(db_author)
        session.commit()
        session.refresh(db_author)

        return db_author
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Author name already exists',
        )


@router.delete(
    '/{author_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_author(
    author_id: int,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    db_author = session.scalar(select(Author).where(Author.id == author_id))

    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )

    session.delete(db_author)
    session.commit()

    return {'message': 'Author deleted'}


@router.patch(
    '/{author_id}', status_code=HTTPStatus.OK, response_model=AuthorPublic
)
def update_author(
    author_id: int,
    new_author: AuthorSchema,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    author_name = sanitize_string(new_author.name)

    db_author = session.scalar(select(Author).where(Author.id == author_id))
    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )

    try:
        db_author.name = author_name
        session.commit()
        session.refresh(db_author)

        return db_author
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Author name already exists',
        )


@router.get(
    '/{author_id}', status_code=HTTPStatus.OK, response_model=AuthorPublic
)
def read_author_detail(
    author_id: int, session: Session = Depends(get_session)
):
    db_author = session.scalar(select(Author).where(Author.id == author_id))

    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )

    return db_author


@router.get('/', status_code=HTTPStatus.OK, response_model=AuthorList)
def read_authors(
    session: Session = Depends(get_session),
    filter_page: AuthorsFilterPage = Depends(),
):
    query = select(Author)
    if filter_page.name:
        name_filter = sanitize_string(filter_page.name)
        query = query.where(Author.name.contains(name_filter))

    authors = session.scalars(
        query.offset(filter_page.offset).limit(filter_page.limit)
    ).all()

    return {'authors': authors}
