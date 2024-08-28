from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy import RowMapping, delete, insert, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self, skip: Optional[int], limit: Optional[int], **filter_by
    ) -> List[RowMapping]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, **filter_by) -> Optional[RowMapping]:
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict, **filter_by) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int) -> RowMapping:
        raise NotImplementedError

    # @abstractmethod
    # async def delete_many(self, **filters) -> None:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # async def count_all(self, **filter_by) -> int:
    #     raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_one(self, id: int, data: dict) -> int:
        stmt = (
            update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_all(self):
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_one_or_none(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_one(self, id: int) -> RowMapping:
        stmt = delete(self.model).filter_by(id=id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
