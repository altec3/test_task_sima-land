from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy import CursorResult, exc, Row

from app.database.schemas import user, role
from app.services.pas import PasService
from app.settings import config


# TODO: Реализовать аутентификацию и авторизацию
# TODO: Перейти на CBV
# TODO: Реализовать сериализацию данных
async def user_create(request: Request) -> web.Response:
    """
    201 Created, 400 Bad Request
    """
    pas_service = PasService(config)
    data: dict = await request.json()
    data['password'] = await pas_service.encode_password(data.get('password'))
    user_role: str = data.pop('role', None)
    try:
        async with request.app['db'].begin() as conn:
            if user_role:
                result: CursorResult = await conn.execute(role.insert(), {'role': user_role.lower()})
            else:
                result: CursorResult = await conn.execute(role.insert())
            roles_id = result.inserted_primary_key[0]
            data['roles_id'] = roles_id
            result: CursorResult = await conn.execute(user.insert().values(**data).returning(user))
            created_user = result.first()
            data = {
                'id': created_user.id,
                'first_name': created_user.first_name,
                'last_name': created_user.last_name,
                'username': created_user.username,
                'date_of_birth': created_user.date_of_birth,
                'created': str(created_user.created),
                'roles_id': created_user.roles_id,
            }
            return web.json_response(
                data={'status': 'Created', 'data': data},
                headers={'Location': str(request.url.joinpath(f'{data["id"]}'))},
                status=201
            )
    except Exception as exception:
        return web.json_response(data={'status': 'Bad Request', 'detail': exception.args}, status=400)


async def users_list(request) -> web.Response:
    async with request.app['db'].connect() as conn:
        users: CursorResult = await conn.execute(user.select())
        users_data = []
        for row in users:
            users_data.append({
                'id': row.id,
                'first_name': row.first_name,
                'last_name': row.last_name,
                'username': row.username,
                'date_of_birth': row.date_of_birth,
                'created': str(row.created),
                'roles_id': row.roles_id,
            })
        return web.json_response(data={'status': 'OK', 'users': users_data}, status=200)


async def user_retrieve(request: Request) -> web.Response:
    """
    200 OK, 404 Not Found
    """
    user_id = int(request.match_info['user_id'])
    try:
        async with request.app['db'].connect() as conn:
            result: CursorResult = await conn.execute(user.select().where(user.c.id == user_id))
            user_data: Row = result.first()
            if not user_data:
                raise exc.NoResultFound('Object Not Found')
            data = {
                'id': user_data.id,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'username': user_data.username,
                'date_of_birth': user_data.date_of_birth,
                'created': str(user_data.created),
                'roles_id': user_data.roles_id,
            }
            return web.json_response(data={'status': 'OK', 'data': data}, status=200)

    except exc.NoResultFound as exception:
        return web.json_response(data={'status': 'Not Found', 'detail': exception.args}, status=404)


async def user_update(request: Request) -> web.Response:
    """
    204 No Content, 400 Bad Request, 404 Not Found
    """
    user_id = int(request.match_info['user_id'])
    data: dict = await request.json()
    try:
        async with request.app['db'].begin() as conn:
            result: CursorResult = await conn.execute(
                user.update().where(user.c.id == user_id).values(**data).returning(user))
            updated_data: Row = result.first()
            if not updated_data:
                raise exc.NoResultFound('Object Not Found')
            return web.Response(status=204)

    except exc.NoResultFound as exception:
        return web.json_response(data={'status': 'Not Found', 'detail': exception.args}, status=404)

    except Exception as exception:
        return web.json_response(data={'status': 'Bad Request', 'detail': exception.args}, status=400)


async def user_delete(request: Request) -> web.Response:
    """
    204 No Content, 404 Not Found
    """
    user_id = int(request.match_info['user_id'])
    try:
        async with request.app['db'].begin() as conn:
            await conn.execute(role.delete().where(role.c.id == user.c.roles_id).where(user.c.id == user_id))
            result: CursorResult = await conn.execute(user.delete().where(user.c.id == user_id).returning(user))
            deleted_user: Row = result.first()
            if not deleted_user:
                raise exc.NoResultFound('Object Not Found')
            return web.Response(status=204)
    except exc.NoResultFound as exception:
        return web.json_response(data={'status': 'Not Found', 'detail': exception.args}, status=404)


async def role_create(request: Request) -> web.Response:
    """
    201 Created, 400 Bad Request
    """
    data: dict = await request.json()
    try:
        async with request.app['db'].begin() as conn:
            result: CursorResult = await conn.execute(role.insert().values(**data).returning(role))
            created_role: Row = result.first()
            data = {
                'id': created_role.id,
                'role': created_role.role,
            }
            return web.json_response(
                data={'status': 'Created', 'data': data},
                headers={'Location': str(request.url.joinpath(f'{data["id"]}'))},
                status=201
            )
    except Exception as e:
        return web.json_response(data={'status': 'Bad Request', 'detail': e.args}, status=400)


async def roles_list(request) -> web.Response:
    async with request.app['db'].connect() as conn:
        roles: CursorResult = await conn.execute(role.select())
        roles_data = []
        for row in roles:
            roles_data.append({
                'id': row.id,
                'role': row.role,
            })
        return web.json_response(data={'status': 'OK', 'roles': roles_data}, status=200)


async def role_retrieve(request: Request) -> web.Response:
    """
    200 OK, 404 Not Found
    """
    role_id = int(request.match_info['role_id'])
    try:
        async with request.app['db'].connect() as conn:
            result: CursorResult = await conn.execute(role.select().where(role.c.id == role_id))
            role_data: Row = result.first()
            if not role_data:
                raise exc.NoResultFound('Object Not Found')
            data = {
                'id': role_data.id,
                'role': role_data.role,
            }
            return web.json_response(data={'status': 'OK', 'data': data}, status=200)
    except exc.NoResultFound as e:
        return web.json_response(data={'status': 'Not Found', 'detail': e.args}, status=404)


async def role_update(request: Request) -> web.Response:
    """
    204 No Content, 400 Bad Request, 404 Not Found
    """
    role_id = int(request.match_info['role_id'])
    data: dict = await request.json()
    try:
        async with request.app['db'].begin() as conn:
            result: CursorResult = await conn.execute(
                role.update().where(role.c.id == role_id).values(**data).returning(role))
            updated_data: Row = result.first()
            if not updated_data:
                raise exc.NoResultFound('Object Not Found')
            return web.Response(status=204)
    except exc.NoResultFound as e:
        return web.json_response(data={'status': 'Not Found', 'detail': e.args}, status=404)
    except Exception as e:
        return web.json_response(data={'status': 'Bad Request', 'detail': e.args}, status=400)


async def role_delete(request: Request) -> web.Response:
    """
    204 No Content, 404 Not Found
    """
    role_id = int(request.match_info['role_id'])
    try:
        async with request.app['db'].begin() as conn:
            result: CursorResult = await conn.execute(role.delete().where(role.c.id == role_id).returning(role))
            deleted_role: Row = result.first()
            if not deleted_role:
                raise exc.NoResultFound('Object Not Found')
            return web.Response(status=204)
    except exc.NoResultFound as e:
        return web.json_response(data={'status': 'Not Found', 'detail': e.args}, status=404)
