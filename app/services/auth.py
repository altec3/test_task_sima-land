import calendar
import datetime

import jwt
from aiohttp import web

from app.services.pas import PasService
from app.services.role import RoleService
from app.services.user import UserService


class AuthService:
    def __init__(self,
                 config: dict[str, dict],
                 user_service: UserService,
                 role_service: RoleService,
                 pas_service: PasService
                 ):

        self._config = config
        self._user_service = user_service
        self._role_service = role_service
        self._pas_service = pas_service

    async def _get_options(self) -> dict[str, str]:
        return self._config['jwt']

    async def _check_credentials(self, credentials: dict[str, str], is_refresh: bool = False) -> dict[str, str]:
        username: str = credentials.get('username', None)
        password: str = credentials.get('password', None)

        # Check user
        user: dict | None = await self._user_service.get_by_username(username)
        if not user:
            raise web.HTTPBadRequest

        if not is_refresh:
            # Check password
            if not await self._pas_service.compare_passwords(user['password'], password):
                raise web.HTTPBadRequest

        # TODO: Рассмотреть возможность применения JOIN (при запросе user)
        role: dict = await self._role_service.get_by_id(user['roles_id'])
        user['role'] = role['role']

        return user

    async def generate_tokens(self, auth_data: dict, is_refresh: bool = False) -> dict[str, str]:
        options: dict[str, str] = await self._get_options()

        user: dict = await self._check_credentials(auth_data, is_refresh)

        data = {
            'username': user['username'],
            'role': user['role'],
        }

        # Access token generation
        exp_min = datetime.datetime.utcnow() + datetime.timedelta(minutes=float(options['exp_min']))
        data['exp'] = calendar.timegm(exp_min.timetuple())
        access_token = jwt.encode(payload=data, key=options['secret'], algorithm=options['algorithm'])

        # Refresh token generation
        exp_days = datetime.datetime.utcnow() + datetime.timedelta(days=float(options['exp_days']))
        data['exp'] = calendar.timegm(exp_days.timetuple())
        refresh_token = jwt.encode(payload=data, key=options['secret'], algorithm=options['algorithm'])

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    async def approve_refresh_token(self, token: str) -> dict[str, str]:
        options: dict[str, str] = await self._get_options()
        refresh_token: str = token
        data: dict[str, str] = jwt.decode(jwt=refresh_token, key=options['secret'], algorithms=[options['algorithm']])

        return await self.generate_tokens(auth_data=data, is_refresh=True)
