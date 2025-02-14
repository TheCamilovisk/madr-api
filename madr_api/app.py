from http import HTTPStatus

from fastapi import FastAPI

from madr_api.routers import accounts, auth, authors, books
from madr_api.schemas import Message

app = FastAPI()

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(books.router)
app.include_router(authors.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}
