from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_pydantic import PydanticView

from dao.role import RoleDAO
from dao.user import UserDAO
from middlewares import owner_or_admin_required, admin_required
from views.models import UserRegisterModel, UserEditModel, UserRetrieveModel
from services.role import RoleService
from services.user import UserService


async def user_register(request: Request) -> web.Response:
    """
    ---
    description: Create a new user with user role.
    tags:
    - Users
    produces:
    - application/json
    responses:
        "201":
            description: Successful operation. Created
        "400":
            description: Bad Request
    """
    data: dict = await request.json()
    data = UserRegisterModel.validate(data).dict()

    async with request.app['db'].begin() as conn:
        role_dao = RoleDAO(conn)
        user_dao = UserDAO(conn)
        role_service = RoleService(role_dao)
        user_service = UserService(user_dao)

        created_role: dict | None = await role_service.create()
        if not created_role:
            raise web.HTTPBadRequest()

        roles_id = created_role['id']
        data['roles_id'] = roles_id

        created_user: dict | None = await user_service.create(data)
        if not created_user:
            raise web.HTTPBadRequest()
        created_user = UserRetrieveModel.validate(created_user).dict()

        return web.json_response(
            data={'status': 'Created', 'data': created_user},
            headers={'Location': str(request.url.joinpath(f'{created_user["id"]}'))},
            status=201
        )


@admin_required
class UsersCollectView(PydanticView):
    async def get(self) -> web.Response:
        """
        ---
        description: Get list of users.
        tags:
        - Users
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation
        """
        async with self.request.app['db'].connect() as connection:
            user_dao = UserDAO(connection)
            user_service = UserService(user_dao)

            users: list[dict] = await user_service.get_all()
            users = [UserRetrieveModel.validate(user).dict() for user in users]

            return web.json_response(data={'status': 'OK', 'users': users}, status=200)

    async def post(self, user: UserRegisterModel) -> web.Response:
        """
        ---
        description: Create a new user.
        tags:
        - Users
        produces:
        - application/json
        responses:
            "201":
                description: Successful operation. Created
            "400":
                description: Bad Request
        """
        data: dict = user.dict(exclude_unset=True)

        async with self.request.app['db'].begin() as connection:
            user_dao = UserDAO(connection)
            role_dao = RoleDAO(connection)
            user_service = UserService(user_dao)
            role_service = RoleService(role_dao)

            created_role: dict | None = await role_service.create()
            if not created_role:
                raise web.HTTPBadRequest()

            roles_id = created_role['id']
            data['roles_id'] = roles_id

            created_user: dict | None = await user_service.create(data)
            if not created_user:
                raise web.HTTPBadRequest()
            created_user = UserRetrieveModel.validate(created_user).dict()

            return web.json_response(
                data={'status': 'Created', 'data': created_user},
                headers={'Location': str(self.request.url.joinpath(f'{created_user["id"]}'))},
                status=201
            )


@owner_or_admin_required
class UserItemView(PydanticView):
    async def get(self, uid: int, /) -> web.Response:
        """
        ---
        description: Get a user by ID.
        tags:
        - Users
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation
            "404":
                description: Not Found
        """
        user_id = uid
        async with self.request.app['db'].connect() as connection:
            user_dao = UserDAO(connection)
            user_service = UserService(user_dao)

            user_data: dict | None = await user_service.get_by_id(user_id)
            if not user_data:
                raise web.HTTPNotFound()

            user_data = UserRetrieveModel.validate(user_data).dict()

            return web.json_response(data={'status': 'OK', 'data': user_data}, status=200)

    async def patch(self, uid: int, /, user: UserEditModel) -> web.Response:
        """
        ---
        description: Update a user by id.
        tags:
        - Users
        responses:
            "204":
                description: Successful operation. No Content
            "400":
                description: Bad Request
            "404":
                description: Not Found
        """

        data: dict = user.dict(exclude_unset=True)
        data['id'] = uid

        async with self.request.app['db'].begin() as connection:
            user_dao = UserDAO(connection)
            user_service = UserService(user_dao)

            updated_data: bool | None = await user_service.update(data)
            if isinstance(updated_data, bool) and not updated_data:
                raise web.HTTPBadRequest()
            if not updated_data:
                raise web.HTTPNotFound()

            return web.Response(status=204)

    async def delete(self, uid: int, /) -> web.Response:
        """
        ---
        description: Delete user by id.
        tags:
        - Users
        responses:
            "204":
                description: Successful operation. No Content
            "404":
                description: Not Found
        """
        user_id = uid
        async with self.request.app['db'].begin() as connection:
            role_dao = RoleDAO(connection)
            user_dao = UserDAO(connection)
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
