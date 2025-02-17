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


class AuthorSchema(BaseModel):
    name: str


class AuthorPublic(BaseModel):
    id: int
    name: str


class AuthorList(BaseModel):
    authors: list[AuthorPublic]


class AuthorsFilterPage(FilterPage):
    name: str = ''


class BookSchema(BaseModel):
    title: str
    year: int
    author_id: int


class BookPublic(BookSchema):
    id: int


class BookUpdate(BaseModel):
    title: str | None = None
    year: int | None = None
    author_id: int | None = None


class BookList(BaseModel):
    books: list[BookPublic]


class BooksFilterPage(FilterPage):
    title: str | None = None
    year: int | None = None
