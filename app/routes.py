from users.views import (user_create, users_list, user_update, user_delete, user_retrieve,
                         role_create, roles_list, role_update, role_delete, role_retrieve)


def setup_routes(app):
    app.router.add_post('/users', user_create)
    app.router.add_get('/users', users_list)
    app.router.add_get(r'/users/{user_id:\d+}', user_retrieve)
    app.router.add_patch(r'/users/{user_id:\d+}', user_update)
    app.router.add_delete(r'/users/{user_id:\d+}', user_delete)
    app.router.add_post('/roles', role_create)
    app.router.add_get('/roles', roles_list)
    app.router.add_get(r'/roles/{role_id:\d+}', role_retrieve)
    app.router.add_patch(r'/roles/{role_id:\d+}', role_update)
    app.router.add_delete(r'/roles/{role_id:\d+}', role_delete)
