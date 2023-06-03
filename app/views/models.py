from pydantic import BaseModel, PositiveInt


class RoleModel(BaseModel):
    """
    Model for validate role request data
    """
    role = 'user'


class UserRegisterModel(BaseModel):
    """
    Model for validate user registration request data
    """
    username: str
    password: str


class UserEditModel(BaseModel):
    """
    Model for validate user update request data
    """
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    date_of_birth: str | None = None


class RoleRetrieveModel(BaseModel):
    """
    Model for serialize role response data
    """
    id: PositiveInt
    role: str


class UserRetrieveModel(BaseModel):
    """
    Model for serialize user response data
    """
    id: PositiveInt
    first_name: str | None = None
    last_name: str | None = None
    username: str
    date_of_birth: str | None = None
    roles_id: PositiveInt
