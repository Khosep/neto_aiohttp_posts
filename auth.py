import base64
import json
import bcrypt
from aiohttp import web
from models import User, Session
from sqlalchemy.future import select


def hash_password(password: str) -> str:
    return (bcrypt.hashpw(password.encode(), bcrypt.gensalt())).decode()


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def get_username_password_from_authdata(auth_from_headers: str) -> tuple:
    """ Получаем username и password из headers"""
    auth_data = auth_from_headers.split()[1]
    un_h, psw_h = base64.b64decode(auth_data.encode()).decode().split(':')
    return un_h, psw_h


async def is_authenticated(username: str, password: str):
    """Проверка аутентификации"""
    async with Session() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().one_or_none()
        if user:
            user_id = user.id
            db_password = user.password
            if check_password(password, db_password):
                return user_id
            else:
                raise web.HTTPForbidden(content_type='application/json',
                                        text=json.dumps({'status': 'error',
                                                         'message': 'wrong password'}))
        else:
            raise web.HTTPForbidden(content_type='application/json',
                                    text=json.dumps({'status': 'error',
                                                     'message': 'wrong username'}))


async def total_check_authentication(auth_from_headers: str):
    username, password = get_username_password_from_authdata(auth_from_headers)
    user_id = await is_authenticated(username, password)
    return user_id
