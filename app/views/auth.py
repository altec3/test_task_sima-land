import aiohttp_session
from aiohttp import web

from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.services.auth import AuthService
from app.services.pas import PasService
from app.services.role import RoleService
from app.services.user import UserService
from app.settings import config


class AuthView(web.View):
    async def post(self):
        """
            ---
            description: This end-point allow to authenticate a user with a username and password.
            tags:
            - Auth
            produces:
            - application/json
            responses:
                "201":
                    description: Successful operation. Returns a pair of tokens (access и refresh)
                "400":
                    description: Bad Request
            """

        await aiohttp_session.new_session(self.request)
        data: dict = await self.request.json()
        username: str = data['username']
        password: str = data['password']

        if None in [username, password]:
            assert web.HTTPBadRequest()

        async with self.request.app['db'].connect() as connection:
            role_dao = RoleDAO(connection)
            user_dao = UserDAO(connection)
            role_service = RoleService(role_dao)
            user_service = UserService(user_dao)
            pas_service = PasService(config)
            auth_service = AuthService(config, user_service, role_service, pas_service)

            tokens: dict = await auth_service.generate_tokens(data)

        return web.json_response(data=tokens, status=201)

    async def put(self):
        """
        ---
        description: This end-point allow to reauthenticate a user with a refresh token.
        tags:
        - Auth
        produces:
        - application/json
        responses:
            "201":
                description: Successful operation. Returns a pair of tokens (access и refresh)
            "400":
                description: Bad Request
        """

        await aiohttp_session.new_session(self.request)
        data: dict = await self.request.json()
        refresh_token: str = data.get('refresh_token', None)
        if not refresh_token:
            assert web.HTTPBadRequest()

        async with self.request.app['db'].connect() as connection:
            role_dao = RoleDAO(connection)
            user_dao = UserDAO(connection)
            role_service = RoleService(role_dao)
            user_service = UserService(user_dao)
            pas_service = PasService(config)
            auth_service = AuthService(config, user_service, role_service, pas_service)

            tokens: dict = await auth_service.approve_refresh_token(refresh_token)

        return web.json_response(data=tokens, status=201)


async def logout(request: web.Request) -> web.Response:
    """ Logout. Clear session """

    session = await aiohttp_session.get_session(request)
    session.clear()
    return web.HTTPSeeOther(location='/login')
