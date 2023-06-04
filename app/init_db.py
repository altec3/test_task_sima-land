import base64
import hashlib

from sqlalchemy import create_engine, MetaData, CursorResult, Row, exc

from dao.database.schemas import user, role
from settings import config

DSN = 'postgresql://{user}:{password}@{host}:{port}/{database}'


def _encode_password(password: str) -> str:
    options = config['hashlib']
    salt = options['salt']

    hash_digest = hashlib.pbkdf2_hmac(
        hash_name=options['hash_name'],
        password=password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        iterations=int(options['iterations'])
    )

    return base64.b64encode(hash_digest).decode('utf-8')


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[user, role])


def create_admin(engine):
    connection = engine.connect()
    try:
        # Create admin role
        result: CursorResult = connection.execute(role.insert().values({'role': 'admin'}).returning(role))
        created_role: Row[role] = result.first()
        # Create admin
        password = _encode_password(str(config['common']['admin_password']))
        connection.execute(user.insert().values({
            'username': config['common']['admin_username'],
            'password': password,
            'roles_id': created_role.id
        }))
        connection.commit()
    except exc.SQLAlchemyError:
        connection.rollback()
    finally:
        connection.close()


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url, echo=True)

    # Создает таблицы в БД
    create_tables(engine)
    # Создает пользователя с админскими правами
    create_admin(engine)
