from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_api.database import get_session
from madr_api.models import UserAccount
from madr_api.settings import Settings

pwd_context = PasswordHash.recommended()

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode |= {'exp': expire}
    print(to_encode)
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user_account(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validade credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception

    account = session.scalar(
        select(UserAccount).where(UserAccount.email == subject_email)
    )
    if not account:
        raise credentials_exception

    return account
