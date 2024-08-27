
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.transactions import TransactionResponse, TransactionSchemaAdd
from app.utils.dependencies import UnitOfWork
from app.repositories.transactions import TransactionRepository


class TransactionsService:
    @staticmethod
    async def get_all_transactions(uow: UnitOfWork) -> list[TransactionResponse]:
        async with (uow):
            transactions = await uow.transactions.find_all()
            if not transactions:
                raise HTTPException(status_code=404, detail="Transactions not found")

            return transactions

    @staticmethod
    async def get_transaction_by_id(uow: UnitOfWork, transaction_id: int) -> TransactionResponse:
        async with uow:
            transaction = await uow.transactions.find_one_or_none(id=transaction_id)
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            return transaction

    @staticmethod
    async def get_transactions_by_user_id(uow: UnitOfWork, user_id: int) -> list[TransactionResponse]:
        async with uow:
            transactions = await uow.transactions.find_by_user_id(user_id=user_id)

            return transactions


    @staticmethod
    async def add_transaction(uow: UnitOfWork, transaction_data: TransactionSchemaAdd) -> TransactionResponse:
        async with uow:
            transaction_dict = transaction_data.model_dump()
            transaction_id = await uow.transactions.add_one(transaction_dict)
            user.balance += transaction_data.amount
            uow.session.add(user)
            await uow.commit()
            await uow.session.refresh(user)
            return transaction_id



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



