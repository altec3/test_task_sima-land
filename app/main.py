from aiohttp import web
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
import base64

from dao.database.schemas import pg_context
from middlewares import check_auth, check_admin, check_owner_or_admin
from settings import config
from routes import setup_routes


def setup_config(application: web.Application) -> None:
    application['config'] = config


def setup_session(application: web.Application) -> None:
    fernet_key: bytes = fernet.Fernet.generate_key()
    secret_key: bytes = base64.urlsafe_b64decode(fernet_key)
    aiohttp_session.setup(application, EncryptedCookieStorage(secret_key))


def setup_app(application: web.Application) -> web.Application:
    setup_config(application)
    setup_routes(application)
    application.cleanup_ctx.append(pg_context)
    setup_session(application)
    application.middlewares.append(check_auth)
    application.middlewares.append(check_admin)
    application.middlewares.append(check_owner_or_admin)
    return application


if __name__ == '__main__':
    app = web.Application()
    web.run_app(setup_app(app))
