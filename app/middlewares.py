from typing import Callable, Awaitable
from aiohttp import web
import jwt

from app.settings import config

_WebHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]
OPTIONS = config['jwt']


def login_required(func: _WebHandler) -> _WebHandler:
    """ Декоратор, указывающий на необходимость аутентификации"""

    func.__login_required__ = True
    return func


@web.middleware
async def check_login(request: web.Request, handler: _WebHandler) -> web.StreamResponse:
    """ Функция проверки наличия аутентификации """

    require_login: bool = getattr(handler, '__login_required__', False)
    if require_login:
        if not request.headers.get('Authorization'):
            raise web.HTTPUnauthorized()
        token: str = request.headers.get('Authorization')
        if token.startswith('Bearer'):
            token = token.split('Bearer ')[-1]
        try:
            jwt.decode(jwt=token, key=OPTIONS['secret'], algorithms=[OPTIONS['algorithm']])
        except jwt.exceptions:
            raise web.HTTPUnauthorized
    return await handler(request)
