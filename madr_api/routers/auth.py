from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_api.database import get_session
from madr_api.models import UserAccount
from madr_api.schemas import Token
from madr_api.security import (
    create_access_token,
    get_current_user_account,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    account = session.scalar(
        select(UserAccount).where(UserAccount.username == form_data.username)
    )
    if not (
        (account is not None)
        and verify_password(form_data.password, account.password)
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': account.username})

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/refresh_token', status_code=HTTPStatus.OK, response_model=Token)
def get_refresh_token(
    session: Session = Depends(get_session),
    current_account: UserAccount = Depends(get_current_user_account),
):
    access_token = create_access_token(data={'sub': current_account.username})
    return {'access_token': access_token, 'token_type': 'bearer'}
