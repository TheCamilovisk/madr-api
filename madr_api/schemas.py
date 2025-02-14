from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserAccountSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserAccountPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserAccountList(BaseModel):
    accounts: list[UserAccountPublic]


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class Token(BaseModel):
    access_token: str
    token_type: str
