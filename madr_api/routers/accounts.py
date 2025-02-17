from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from madr_api.database import get_session
from madr_api.models import UserAccount
from madr_api.schemas import (
    FilterPage,
    Message,
    UserAccountList,
    UserAccountPublic,
    UserAccountSchema,
)
from madr_api.security import get_current_user_account, get_password_hash

router = APIRouter(prefix='/accounts', tags=['accounts'])


@router.get('/', status_code=HTTPStatus.OK, response_model=UserAccountList)
def read_users(
    filter_page: FilterPage = Depends(),
    session: Session = Depends(get_session),
):
    accounts = session.scalars(
        select(UserAccount).offset(filter_page.offset).limit(filter_page.limit)
    ).all()
    return {'accounts': accounts}


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=UserAccountPublic
)
def create_accout(
    account: UserAccountSchema, session: Session = Depends(get_session)
):
    db_account = session.scalar(
        select(UserAccount).where(
            (UserAccount.username == account.username)
            | (UserAccount.email == account.email)
        )
    )

    if db_account:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )

    db_account = UserAccount(
        username=account.username,
        email=account.email,
        password=get_password_hash(account.password),
    )
    session.add(db_account)
    session.commit()
    session.refresh(db_account)

    return db_account


@router.put(
    '/{account_id}',
    status_code=HTTPStatus.OK,
    response_model=UserAccountPublic,
)
def update_account(
    account_id: int,
    account: UserAccountSchema,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    if account_id != current_account.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    try:
        current_account.username = account.username
        current_account.email = account.email
        current_account.password = get_password_hash(account.password)
        session.commit()
        session.refresh(current_account)

        return current_account
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@router.delete(
    '/{account_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_account(
    account_id: int,
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    session.delete(current_account)
    session.commit()

    return {'message': 'Account deleted'}
