
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.transactions import TransactionResponse, TransactionSchemaAdd
from app.utils.dependencies import UnitOfWork
from app.repositories.transactions import TransactionRepository


class TransactionsService:
    """
    Service class for handling transaction-related operations.
    """
    @staticmethod
    async def get_all_transactions(uow: UnitOfWork) -> list[TransactionResponse]:
        """
        Retrieves all transactions from the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            list[TransactionResponse]: A list of all transactions.

        Raises:
            HTTPException: If no transactions are found.
        """
        async with (uow):
            transactions = await uow.transactions.find_all()
            if not transactions:
                raise HTTPException(status_code=404, detail="Transactions not found")

            return transactions

    @staticmethod
    async def get_transaction_by_id(uow: UnitOfWork, transaction_id: int) -> TransactionResponse:
        """
        Retrieves a specific transaction by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            transaction_id (int): The ID of the transaction to be retrieved.

        Returns:
            TransactionResponse: The transaction data.

        Raises:
            HTTPException: If the transaction with the specified ID is not found.
        """
        async with uow:
            transaction = await uow.transactions.find_one_or_none(id=transaction_id)
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            return transaction

    @staticmethod
    async def get_transactions_by_user_id(uow: UnitOfWork, user_id: int) -> list[TransactionResponse]:
        """
        Retrieves all transactions for a specific user.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user_id (int): The ID of the user whose transactions are to be retrieved.

        Returns:
            list[TransactionResponse]: A list of transactions for the specified user.
        """
        async with uow:
            transactions = await uow.transactions.find_by_user_id(user_id=user_id)

            return transactions


    @staticmethod
    async def add_transaction(uow: UnitOfWork, amount: float, user_id: int) -> TransactionResponse:
        """
        Adds a new transaction and updates the user's balance.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            amount (float): The amount of the transaction.
            user_id (int): The ID of the user associated with the transaction.

        Returns:
            TransactionResponse: The newly created transaction data.

        Raises:
            HTTPException: If the user is not found, or if there is an error during the transaction creation.
        """
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            try:
                transaction_data = {
                    "amount": amount,
                    "user_id": user_id
                }
                
                transaction_id = await uow.transactions.add_one(transaction_data)
                user.balance += amount
                await uow.commit()
                                
                transaction = await uow.transactions.find_one_or_none(id=transaction_id)
                if not transaction:
                    raise HTTPException(status_code=404, detail="Transaction not found after creation")
                
                return TransactionResponse(id=transaction.id, amount=transaction.amount)
            except SQLAlchemyError as e:
                await uow.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



    # @staticmethod
    # async def add_transaction(uow: UnitOfWork, transaction_data: TransactionSchemaAdd) -> int:
    #     async with uow:
    #         transaction_dict = transaction_data.model_dump()

    #         user = await uow.users.find_one_or_none(id=transaction_data.user_id)
    #         if not user:
    #             raise HTTPException(status_code=404, detail="User not found")
    #         try:
    #             transaction_id = await uow.transactions.add_one(transaction_dict)
    #             user.balance += transaction_data.amount
    #             uow.session.add(user)
    #             await uow.commit()
    #             await uow.session.refresh(user)
    #             return transaction_id

    #         except SQLAlchemyError as e:
    #             uow.session.rollback()
    #             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def delete_transaction(uow: UnitOfWork, transaction_id: int):
        """
        Deletes a transaction and updates the user's balance.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            transaction_id (int): The ID of the transaction to be deleted.

        Returns:
            TransactionResponse: The deleted transaction data.

        Raises:
            HTTPException: If the transaction or user is not found, or if there is an error during the deletion.
        """
        async with uow:
            transaction = await uow.transactions.find_one_or_none(id=transaction_id)
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")
            user = await uow.users.find_one_or_none(id=transaction.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            try:
                user.balance -= transaction.amount
                uow.session.add(user)
                await uow.commit()
                await uow.session.refresh(user)
                await uow.transactions.delete_one(id=transaction_id)
                return transaction
            except SQLAlchemyError as e:
                uow.session.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



