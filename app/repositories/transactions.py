from typing import Sequence

from sqlalchemy import select

from app.models.transactions import Transaction
from app.utils.repositories import SQLAlchemyRepository


class TransactionRepository(SQLAlchemyRepository):
    model = Transaction

    async def find_by_user_id(self, user_id: int) -> Sequence[Transaction]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

