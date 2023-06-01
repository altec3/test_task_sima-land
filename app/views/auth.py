import aiohttp_session
from aiohttp import web

from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.services.auth import AuthService
from app.services.pas import PasService
from app.services.role import RoleService
from app.services.user import UserService
from app.settings import config


async def login(request: web.Request) -> web.Response:
    """
    Аутентификация пользователя (JWT).
    Отдает пару токенов (access и refresh)
    """

    await aiohttp_session.new_session(request)
    data: dict = await request.json()
    username: str = data['username']
    password: str = data['password']

    if None in [username, password]:
        assert web.HTTPBadRequest()

    async with request.app['db'].connect() as connection:
        role_dao = RoleDAO(connection)
        user_dao = UserDAO(connection)
        role_service = RoleService(role_dao)
        user_service = UserService(user_dao)
        pas_service = PasService(config)
        auth_service = AuthService(config, user_service, role_service, pas_service)

        tokens: dict = await auth_service.generate_tokens(data)

    return web.json_response(data=tokens, status=201)


async def refresh_login(request: web.Request) -> web.Response:
    """
    Аутентификация пользователя по refresh-токену (JWT).
    Отдает пару токенов (access и refresh)
    """

    await aiohttp_session.new_session(request)
    data: dict = await request.json()
    refresh_token: str = data.get('refresh_token', None)
    if not refresh_token:
        assert web.HTTPBadRequest()

    async with request.app['db'].connect() as connection:
        role_dao = RoleDAO(connection)
        user_dao = UserDAO(connection)
        role_service = RoleService(role_dao)
        user_service = UserService(user_dao)
        pas_service = PasService(config)
        auth_service = AuthService(config, user_service, role_service, pas_service)

        tokens: dict = await auth_service.approve_refresh_token(refresh_token)

    return web.json_response(data=tokens, status=201)


async def logout(request: web.Request) -> web.Response:
    session = await aiohttp_session.get_session(request)
    session.clear()
    return web.HTTPSeeOther(location='/login')
