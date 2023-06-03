from aiohttp import web

from views.user import (user_register, UsersCollectView, UserItemView)
from views.role import (RolesCollectView, RoleItemView)
from app.views.auth import AuthView, logout


def setup_routes(application: web.Application) -> None:
    application.router.add_view('/users', UsersCollectView, name='users_collect')
    application.router.add_view(r'/users/{uid:\d+}', UserItemView, name='user_item')
    application.router.add_view('/roles', RolesCollectView, name='roles_collect')
    application.router.add_view(r'/roles/{rid:\d+}', RoleItemView, name='role_item')
    application.router.add_route('POST', '/login/register', user_register, name='user_register')
    application.router.add_view('/login', AuthView, name='user_auth')
    application.router.add_route('GET', '/logout', logout, name='user_logout')
