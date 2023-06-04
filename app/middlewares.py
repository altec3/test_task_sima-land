from typing import Callable, Awaitable

import aiohttp_session
from aiohttp import web
import jwt

from settings import config

_WebHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]
OPTIONS = config['jwt']


def auth_required(func: _WebHandler) -> _WebHandler:
    """ Декоратор, указывающий на необходимость аутентификации """

    func.__auth_required__ = True
    return func


def admin_required(func: _WebHandler) -> _WebHandler:
    """ Декоратор, указывающий на необходимость наличия прав администратора """

    func.__auth_required__ = True
    func.__admin_required__ = True
    return func


def owner_or_admin_required(func: _WebHandler) -> _WebHandler:
    """ Декоратор, указывающий на необходимость наличия прав владельца или администратора """

    func.__auth_required__ = True
    func.__owner_or_admin_required__ = True
    return func


@web.middleware
async def check_auth(request: web.Request, handler: _WebHandler) -> web.StreamResponse:
    """ Функция проверки наличия JWT аутентификации """

    is_required: bool = getattr(handler, '__auth_required__', False)
    if is_required:
        session = await aiohttp_session.get_session(request)
        if not request.headers.get('Authorization'):
            raise web.HTTPUnauthorized()

        token: str = request.headers.get('Authorization')
        if token.startswith('Bearer'):
            token = token.split('Bearer ')[-1]
        try:
            user: dict[str, str] = jwt.decode(jwt=token, key=OPTIONS['secret'], algorithms=[OPTIONS['algorithm']])
            session['user_id'] = int(user.get('id'))
            session['user_role'] = user.get('role', 'user')
        except jwt.exceptions.PyJWTError:
            raise web.HTTPUnauthorized

    return await handler(request)


@web.middleware
async def check_admin(request: web.Request, handler: _WebHandler) -> web.StreamResponse:
    """ Функция проверки наличия прав администратора """

    is_required: bool = getattr(handler, '__admin_required__', False)
    if is_required:
        session = await aiohttp_session.get_session(request)
        try:
            user_role: str = session['user_role']
        except Exception:
            raise web.HTTPUnauthorized

        if user_role != 'admin':
            raise web.HTTPForbidden

    return await handler(request)


@web.middleware
async def check_owner_or_admin(request: web.Request, handler: _WebHandler) -> web.StreamResponse:
    """ Функция проверки наличия прав владельца или администратора """

    is_required: bool = getattr(handler, '__owner_or_admin_required__', False)
    if is_required:
        session = await aiohttp_session.get_session(request)
        requested_id = int(request.match_info['uid'])

        try:
            user_id: int = session['user_id']
            user_role: str = session['user_role']
        except Exception:
            raise web.HTTPUnauthorized

        if True in [user_role == 'admin', requested_id == user_id]:
            return await handler(request)
        else:
            raise web.HTTPForbidden

    return await handler(request)
