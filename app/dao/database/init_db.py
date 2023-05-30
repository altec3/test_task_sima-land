from sqlalchemy import create_engine, MetaData

from app.dao.database.schemas import user, role
from app.settings import config


DSN = 'postgresql://{user}:{password}@{host}:{port}/{database}'


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[user, role])


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url, echo=True)

    # Создает таблицы в БД
    create_tables(engine)
