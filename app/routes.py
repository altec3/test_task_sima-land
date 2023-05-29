from users.views import (UserCreateView, UsersListView, UserUpdateView, UserDeleteView, UserRetrieveView,
                         RoleCreateView, RolesListView, RoleUpdateView, RoleDeleteView, RoleRetrieveView)


def setup_routes(app):
    app.router.add_post('/users', UserCreateView)
    app.router.add_get('/users', UsersListView)
    app.router.add_get(r'/users/{user_id:\d+}', UserRetrieveView)
    app.router.add_patch(r'/users/{user_id:\d+}', UserUpdateView)
    app.router.add_delete(r'/users/{user_id:\d+}', UserDeleteView)
    app.router.add_post('/roles', RoleCreateView)
    app.router.add_get('/roles', RolesListView)
    app.router.add_get(r'/roles/{role_id:\d+}', RoleRetrieveView)
    app.router.add_patch(r'/roles/{role_id:\d+}', RoleUpdateView)
    app.router.add_delete(r'/roles/{role_id:\d+}', RoleDeleteView)
