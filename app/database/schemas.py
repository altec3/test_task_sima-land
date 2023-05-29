from datetime import datetime
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime, Enum,
)
from sqlalchemy.ext.asyncio import create_async_engine

__all__ = ['user', 'role', 'pg_context']

DSN = 'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'

meta = MetaData()


user = Table(
    'users', meta,

    Column('id', Integer, primary_key=True),
    Column('first_name', String(150), nullable=True),
    Column('last_name', String(150), nullable=True),
    Column('username', String(150),  unique=True, nullable=False),
    Column('password', String(200), nullable=False),
    Column('date_of_birth', DateTime(), nullable=True),
    Column('created', DateTime(), default=datetime.now()),
    Column('roles_id', Integer, ForeignKey('roles.id', ondelete='SET NULL'))
)

role = Table(
    'roles', meta,

    Column('id', Integer, primary_key=True),
    Column('role', Enum('user', 'admin', name='role_types'), default='user', nullable=False,),
)


async def pg_context(app):
    conf = app['config']['postgres']
    db_url = DSN.format(**conf)
    engine = create_async_engine(db_url, echo=True,)
    app['db'] = engine

    yield

    app['db'].close()
    await app['db'].wait_closed()
