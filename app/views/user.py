from aiohttp import web
from aiohttp.web_request import Request

from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.middlewares import owner_or_admin_required, admin_required
from app.services.role import RoleService
from app.services.user import UserService


async def user_create(request: Request) -> web.Response:
    """ Создание пользователя """

    data: dict = await request.json()
    user_role: str = data.pop('role'.lower(), None)

    async with request.app['db'].begin() as conn:
        role_dao = RoleDAO(conn)
        user_dao = UserDAO(conn)
        role_service = RoleService(role_dao)
        user_service = UserService(user_dao)

        if user_role:
            created_role: dict | None = await role_service.create({'role': user_role})
        else:
            created_role: dict | None = await role_service.create()
        if not created_role:
            raise web.HTTPBadRequest()

        roles_id = created_role['id']
        data['roles_id'] = roles_id

        created_user: dict | None = await user_service.create(data)
        if not created_user:
            raise web.HTTPBadRequest()

        return web.json_response(
            data={'status': 'Created', 'data': created_user},
            headers={'Location': str(request.url.joinpath(f'{created_user["id"]}'))},
            status=201
        )


@admin_required
async def users_list(request: Request) -> web.Response:
    """ Список пользователей """

    async with request.app['db'].connect() as conn:
        user_dao = UserDAO(conn)
        user_service = UserService(user_dao)

        users: list = await user_service.get_all()

        return web.json_response(data={'status': 'OK', 'users': users}, status=200)


@owner_or_admin_required
async def user_retrieve(request: Request) -> web.Response:
    """ Пользователь по id """

    user_id = int(request.match_info['user_id'])
    async with request.app['db'].connect() as conn:
        user_dao = UserDAO(conn)
        user_service = UserService(user_dao)

        user_data = await user_service.get_by_id(user_id)

        if not user_data:
            raise web.HTTPNotFound()

        return web.json_response(data={'status': 'OK', 'data': user_data}, status=200)


@owner_or_admin_required
async def user_update(request: Request) -> web.Response:
    """ Обновление полей пользователя """

    user_id = int(request.match_info['user_id'])
    data: dict = await request.json()
    data['id'] = user_id
    async with request.app['db'].begin() as conn:
        user_dao = UserDAO(conn)
        user_service = UserService(user_dao)

        updated_data = await user_service.update(data)

        if isinstance(updated_data, bool) and not updated_data:
            raise web.HTTPBadRequest()
        if not updated_data:
            raise web.HTTPNotFound()

        return web.Response(status=204)


@owner_or_admin_required
async def user_delete(request: Request) -> web.Response:
    """ Удаление пользователя """

    user_id = int(request.match_info['user_id'])
    async with request.app['db'].begin() as conn:
        role_dao = RoleDAO(conn)
        user_dao = UserDAO(conn)
        role_service = RoleService(role_dao)
        user_service = UserService(user_dao)

        deleted_user: dict | None = await user_service.delete(user_id)
        if not deleted_user:
            raise web.HTTPNotFound

        role_id = deleted_user['roles_id']
        deleted_role: dict | None = await role_service.delete(role_id)
        if not deleted_role:
            raise web.HTTPNotFound

        return web.Response(status=204)
