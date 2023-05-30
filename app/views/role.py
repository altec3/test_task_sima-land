from aiohttp import web
from aiohttp.web_request import Request

from app.dao.role import RoleDAO
from app.services.role import RoleService


# TODO: Реализовать аутентификацию и авторизацию
# TODO: Перейти на CBV
# TODO: Реализовать сериализацию данных
async def role_create(request: Request) -> web.Response:
    """ Создание роли """

    data: dict = await request.json()
    async with request.app['db'].begin() as conn:
        role_dao = RoleDAO(conn)
        role_service = RoleService(role_dao)

        created_role: dict | None = await role_service.create(data)
        if not created_role:
            raise web.HTTPBadRequest()

        return web.json_response(
            data={'status': 'Created', 'data': created_role},
            headers={'Location': str(request.url.joinpath(f'{created_role["id"]}'))},
            status=201
        )


async def roles_list(request: Request) -> web.Response:
    """ Список ролей """

    async with request.app['db'].connect() as conn:
        role_dao = RoleDAO(conn)
        role_service = RoleService(role_dao)

        roles: list = await role_service.get_all()

        return web.json_response(data={'status': 'OK', 'roles': roles}, status=200)


async def role_retrieve(request: Request) -> web.Response:
    """ Роль по id """

    role_id = int(request.match_info['role_id'])
    async with request.app['db'].connect() as conn:
        role_dao = RoleDAO(conn)
        role_service = RoleService(role_dao)

        role_data: dict | None = await role_service.get_by_id(role_id)
        if not role_data:
            raise web.HTTPNotFound

        return web.json_response(data={'status': 'OK', 'data': role_data}, status=200)


async def role_update(request: Request) -> web.Response:
    """ Обновление роли """

    role_id = int(request.match_info['role_id'])
    data: dict = await request.json()
    data['id'] = role_id
    async with request.app['db'].begin() as conn:
        role_dao = RoleDAO(conn)
        role_service = RoleService(role_dao)

        updated_data: bool | None = await role_service.update(data)
        if isinstance(updated_data, bool) and not updated_data:
            raise web.HTTPBadRequest()
        if not updated_data:
            raise web.HTTPNotFound()

        return web.Response(status=204)


async def role_delete(request: Request) -> web.Response:
    """ Удаление роли """

    role_id = int(request.match_info['role_id'])
    async with request.app['db'].begin() as conn:
        role_dao = RoleDAO(conn)
        role_service = RoleService(role_dao)

        deleted_role: dict | None = await role_service.delete(role_id)
        if not deleted_role:
            raise web.HTTPNotFound

        return web.Response(status=204)
