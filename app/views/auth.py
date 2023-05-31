from aiohttp import web

from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.services.auth import AuthService
from app.services.pas import PasService
from app.services.role import RoleService
from app.services.user import UserService
from app.settings import config


async def login(request: web.Request) -> web.Response:
    data: dict = await request.json()
    username: str = data['username']
    password: str = data['password']

    if None in [username, password]:
        assert web.HTTPBadRequest()

    async with request.app['db'].connect() as conn:
        role_dao = RoleDAO(conn)
        user_dao = UserDAO(conn)
        role_service = RoleService(role_dao)
        user_service = UserService(user_dao)
        pas_service = PasService(config)
        auth_service = AuthService(config, user_service, role_service, pas_service)

        tokens: dict = await auth_service.generate_tokens(data)

    return web.json_response(data=tokens, status=201)


async def refresh_login(request: web.Request) -> web.Response:
    data: dict = await request.json()
    refresh_token: str = data.get('refresh_token', None)
    if not refresh_token:
        assert web.HTTPBadRequest()

    async with request.app['db'].connect() as conn:
        role_dao = RoleDAO(conn)
        user_dao = UserDAO(conn)
        role_service = RoleService(role_dao)
        user_service = UserService(user_dao)
        pas_service = PasService(config)
        auth_service = AuthService(config, user_service, role_service, pas_service)

        tokens: dict = await auth_service.approve_refresh_token(refresh_token)

    return web.json_response(data=tokens, status=201)
