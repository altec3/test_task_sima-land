from aiohttp import web
from aiohttp_pydantic import PydanticView

from dao.role import RoleDAO
from middlewares import admin_required
from views.models import RoleModel, RoleRetrieveModel
from services.role import RoleService


@admin_required
class RolesCollectView(PydanticView):
    async def get(self) -> web.Response:
        """
        ---
        description: Get list of roles.
        tags:
        - Roles
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation
        """
        async with self.request.app['db'].connect() as connection:
            role_dao = RoleDAO(connection)
            role_service = RoleService(role_dao)

            roles: list[dict] = await role_service.get_all()
            roles = [RoleRetrieveModel.validate(role).dict() for role in roles]

            return web.json_response(data={'status': 'OK', 'roles': roles}, status=200)

    async def post(self, role: RoleModel) -> web.Response:
        """
        ---
        description: Create a new role.
        tags:
        - Roles
        produces:
        - application/json
        responses:
            "201":
                description: Successful operation. Created
            "400":
                description: Bad Request
        """
        data: dict = role.dict(exclude_unset=True)
        async with self.request.app['db'].begin() as connection:
            role_dao = RoleDAO(connection)
            role_service = RoleService(role_dao)

            created_role: dict | None = await role_service.create(data)
            if not created_role:
                raise web.HTTPBadRequest()
            created_role = RoleRetrieveModel.validate(created_role).dict()

            return web.json_response(
                data={'status': 'Created', 'data': created_role},
                headers={'Location': str(self.request.url.joinpath(f'{created_role["id"]}'))},
                status=201
            )


@admin_required
class RoleItemView(PydanticView):
    async def get(self, rid: int, /) -> web.Response:
        """
        ---
        description: Get a role by ID.
        tags:
        - Roles
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation
            "404":
                description: Not Found
        """
        role_id = rid
        async with self.request.app['db'].connect() as connection:
            role_dao = RoleDAO(connection)
            role_service = RoleService(role_dao)

            role_data: dict | None = await role_service.get_by_id(role_id)
            if not role_data:
                raise web.HTTPNotFound
            role_data = RoleRetrieveModel.validate(role_data).dict()

            return web.json_response(data={'status': 'OK', 'data': role_data}, status=200)

    async def patch(self, rid: int, /, role: RoleModel) -> web.Response:
        """
        ---
        description: Update a role by ID.
        tags:
        - Roles
        responses:
            "204":
                description: Successful operation. No Content
            "400":
                description: Bad Request
            "404":
                description: Not Found
        """

        role_id = rid
        data: dict = role.dict()
        data['id'] = role_id
        async with self.request.app['db'].begin() as connection:
            role_dao = RoleDAO(connection)
            role_service = RoleService(role_dao)

            updated_data: bool | None = await role_service.update(data)
            if isinstance(updated_data, bool) and not updated_data:
                raise web.HTTPBadRequest()
            if not updated_data:
                raise web.HTTPNotFound()

            return web.Response(status=204)

    async def delete(self, rid: int, /) -> web.Response:
        """
        ---
        description: Delete role by id.
        tags:
        - Roles
        responses:
            "204":
                description: Successful operation. No Content
            "404":
                description: Not Found
        """
        role_id = rid
        async with self.request.app['db'].begin() as connection:
            role_dao = RoleDAO(connection)
            role_service = RoleService(role_dao)

            deleted_role: dict | None = await role_service.delete(role_id)
            if not deleted_role:
                raise web.HTTPNotFound

            return web.Response(status=204)
