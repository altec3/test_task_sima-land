from typing import Sequence

from sqlalchemy import CursorResult, Row, exc
from sqlalchemy.ext.asyncio import AsyncConnection

from dao.database.schemas import user


class UserDAO:

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def create(self, data: dict) -> Row[user] | None:
        try:
            result: CursorResult = await self._connection.execute(
                user.insert().values(**data).returning(user)
            )
        except exc.SQLAlchemyError:
            return None

        return result.first()

    async def get_all(self) -> Sequence[Row[user]]:
        result: CursorResult = await self._connection.execute(user.select())
        return result.fetchall()

    async def get_by_id(self, uid: int) -> Row[user]:
        result: CursorResult = await self._connection.execute(
            user.select().where(user.c.id == uid)
        )
        return result.first()

    async def get_by_username(self, username: str) -> Row[user]:
        result: CursorResult = await self._connection.execute(
            user.select().where(user.c.username == username)
        )
        return result.first()

    async def update(self, data: dict) -> Row[user] | bool:
        uid = data.pop('id')
        try:
            result: CursorResult = await self._connection.execute(
                user.update().where(user.c.id == uid).values(**data).returning(user))
        except exc.SQLAlchemyError:
            return False

        return result.first()

    async def delete(self, uid: int) -> Row[user]:
        result: CursorResult = await self._connection.execute(
            user.delete().where(user.c.id == uid).returning(user)
        )
        return result.first()
