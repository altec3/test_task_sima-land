from typing import Sequence

from sqlalchemy import CursorResult, Row, exc
from sqlalchemy.ext.asyncio import AsyncConnection

from dao.database.schemas import role


class RoleDAO:

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def create(self, data: dict) -> Row[role] | None:
        try:
            if not data:
                result: CursorResult = await self._connection.execute(
                    role.insert().returning(role))
            else:
                result: CursorResult = await self._connection.execute(
                    role.insert().values(**data).returning(role)
                )
        except exc.SQLAlchemyError:
            return None

        return result.first()

    async def get_all(self) -> Sequence[Row[role]]:
        result: CursorResult = await self._connection.execute(role.select())
        return result.fetchall()

    async def get_by_id(self, rid: int) -> Row[role]:
        result: CursorResult = await self._connection.execute(
            role.select().where(role.c.id == rid)
        )
        return result.first()

    async def update(self, data: dict) -> Row[role] | bool:
        rid = data.pop('id')
        try:
            result: CursorResult = await self._connection.execute(
                role.update().where(role.c.id == rid).values(**data).returning(role))
        except exc.SQLAlchemyError:
            return False

        return result.first()

    async def delete(self, rid: int) -> Row[role]:
        result: CursorResult = await self._connection.execute(
            role.delete().where(role.c.id == rid).returning(role)
        )
        return result.first()
