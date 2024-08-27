from app.models.black_list import BlackList
from app.utils.repositories import SQLAlchemyRepository


class BlackListRepository(SQLAlchemyRepository):
    model = BlackList