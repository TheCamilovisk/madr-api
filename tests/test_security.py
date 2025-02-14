from jwt import decode

from madr_api.security import create_access_token, settings


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(
        token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )

    assert decoded['test'] == data['test']
    assert 'exp' in decoded
