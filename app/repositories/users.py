from app.models.users import User
from app.utils.repositories import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User
