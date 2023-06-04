from typing import Dict, Any, Sequence

from sqlalchemy import Row

from dao.role import RoleDAO
from dao.database.schemas import role
from services.pas import PasService
from settings import config

pas_service = PasService(config)


class RoleService:

    def __init__(self, dao: RoleDAO):
        self._dao = dao

    async def create(self, data: dict = None) -> Dict[str, str | Any] | None:
        created_role: Row[role] | None = await self._dao.create(data)

        if not created_role:
            return None

        data = {
            'id': created_role.id,
            'role': created_role.role,
        }
        return data

    async def get_all(self) -> list[dict | None]:
        roles: Sequence[Row[role]] = await self._dao.get_all()
        roles_data = []
        for row in roles:
            roles_data.append({
                'id': row.id,
                'role': row.role,
            })
        return roles_data

    async def get_by_id(self, rid: int) -> Dict[str, str | Any] | None:
        role_data: Row[role] = await self._dao.get_by_id(rid)

        if not role_data:
            return None

        data = {
            'id': role_data.id,
            'role': role_data.role,
        }
        return data

    async def update(self, data: dict) -> bool | None:
        updated_data: Row[role] | bool = await self._dao.update(data)

        if isinstance(updated_data, bool) and not updated_data:
            return False

        if not updated_data:
            return None

        return True

    async def delete(self, rid: int) -> Dict[str, str | Any] | None:
        deleted_role: Row[role] = await self._dao.delete(rid)

        if not deleted_role:
            return None

        data = {
            'id': deleted_role.id,
            'role': deleted_role.role,
        }
        return data
