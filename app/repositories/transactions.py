from typing import Sequence

from sqlalchemy import select

from app.models.transactions import Transaction
from app.utils.repositories import SQLAlchemyRepository


class TransactionRepository(SQLAlchemyRepository):
    """Repository class for managing Transaction objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """
    model = Transaction

    async def find_by_user_id(self, user_id: int) -> Sequence[Transaction]:
        """Finds all transactions associated with a specific user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Sequence[Transaction]: A sequence of Transaction objects.
        """
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    

