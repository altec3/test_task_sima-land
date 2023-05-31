from typing import Dict, Any, Sequence

from sqlalchemy import Row

from app.dao.user import UserDAO
from app.dao.database.schemas import user
from app.services.pas import PasService
from app.settings import config

pas_service = PasService(config)


class UserService:

    def __init__(self, dao: UserDAO):
        self._dao = dao

    async def create(self, data: dict) -> Dict[str, str | Any] | None:
        data['password'] = await pas_service.encode_password(data.get('password'))
        created_user: Row[user] = await self._dao.create(data)

        if not created_user:
            return None

        data = {
            'id': created_user.id,
            'first_name': created_user.first_name,
            'last_name': created_user.last_name,
            'username': created_user.username,
            'date_of_birth': created_user.date_of_birth,
            'created': str(created_user.created),
            'roles_id': created_user.roles_id,
        }

        return data

    async def get_all(self) -> list[dict | None]:
        users: Sequence[Row[user]] = await self._dao.get_all()
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
        return users_data

    async def get_by_id(self, uid: int) -> Dict[str, str | Any] | None:
        user_data: Row[user] = await self._dao.get_by_id(uid)

        if not user_data:
            return None

        data = {
            'id': user_data.id,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'username': user_data.username,
            'password': user_data.password,
            'date_of_birth': user_data.date_of_birth,
            'created': str(user_data.created),
            'roles_id': user_data.roles_id,
        }
        return data

    async def get_by_username(self, username: str) -> Dict[str, str | Any] | None:
        user_data: Row[user] = await self._dao.get_by_username(username)

        if not user_data:
            return None

        data = {
            'id': user_data.id,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'username': user_data.username,
            'password': user_data.password,
            'date_of_birth': user_data.date_of_birth,
            'created': str(user_data.created),
            'roles_id': user_data.roles_id,
        }
        return data

    async def update(self, data: dict) -> bool | None:
        updated_data: Row[user] | bool = await self._dao.update(data)

        if isinstance(updated_data, bool) and not updated_data:
            return False

        if not updated_data:
            return None

        return True

    async def delete(self, uid: int) -> Dict[str, str | Any] | None:
        deleted_user: Row = await self._dao.delete(uid)

        if not deleted_user:
            return None

        data = {
            'id': deleted_user.id,
            'first_name': deleted_user.first_name,
            'last_name': deleted_user.last_name,
            'username': deleted_user.username,
            'date_of_birth': deleted_user.date_of_birth,
            'created': str(deleted_user.created),
            'roles_id': deleted_user.roles_id,
        }

        return data
