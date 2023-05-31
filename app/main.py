from aiohttp import web

from app.dao.database.schemas import pg_context
from app.middlewares import check_login
from settings import config
from routes import setup_routes


def setup_config(application):
    application['config'] = config


# Функция настройки приложения
def setup_app(application: web.Application):
    setup_config(application)
    setup_routes(application)
    application.cleanup_ctx.append(pg_context)


app = web.Application(middlewares=[check_login])

if __name__ == '__main__':
    setup_app(app)
    web.run_app(app)
