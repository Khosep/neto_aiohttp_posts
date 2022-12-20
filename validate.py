import pydantic
from aiohttp import web

from errors import raise_http_error


class UserCreateValidate(pydantic.BaseModel):
    username: str
    email: str
    password: str


class PostCreateValidate(pydantic.BaseModel):
    title: str
    content: str
    user_id: int


async def validate(data: dict, validate_class):
    try:
        return validate_class(**data).dict()
    except pydantic.ValidationError as er:
        raise raise_http_error(web.HTTPBadRequest, *er.errors())
