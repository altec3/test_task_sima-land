from aiohttp import web

from views.user import (user_create, users_list, user_update, user_delete, user_retrieve)
from views.role import (role_create, roles_list, role_update, role_delete, role_retrieve)
from app.views.auth import login, refresh_login


def setup_routes(application: web.Application) -> None:
    application.router.add_post('/users', user_create)
    application.router.add_get('/users', users_list)
    application.router.add_get(r'/users/{user_id:\d+}', user_retrieve)
    application.router.add_patch(r'/users/{user_id:\d+}', user_update)
    application.router.add_delete(r'/users/{user_id:\d+}', user_delete)
    application.router.add_post('/roles', role_create)
    application.router.add_get('/roles', roles_list)
    application.router.add_get(r'/roles/{role_id:\d+}', role_retrieve)
    application.router.add_patch(r'/roles/{role_id:\d+}', role_update)
    application.router.add_delete(r'/roles/{role_id:\d+}', role_delete)
    application.router.add_post('/login', login)
    application.router.add_put('/login/refresh', refresh_login)
