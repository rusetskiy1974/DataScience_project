from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.models.payments import Payment
from app.schemas.payment import PaymentSchemaAdd, PaymentResponse
from app.utils.dependencies import UnitOfWork
from app.models.payments import TransactionType


class PaymentsService:

    @staticmethod
    async def process_payment(uow: UnitOfWork, payment_data: PaymentSchemaAdd) -> PaymentResponse:
        async with uow:
            user = await uow.users.find_one_or_none(id=payment_data.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            payment_dict = payment_data.model_dump()
            try:
                if payment_data.transaction_type == TransactionType.DEBIT:
                    parking = await uow.parkings.find_one_or_none(id=payment_data.parking_id)
                    if not parking:
                        raise HTTPException(status_code=404, detail="Parking not found")
                    payment = await uow.payments.add_one(payment_dict)

                if payment_data.transaction_type == TransactionType.CREDIT:
                    payment = await uow.payments.add_one(payment_dict)
                    user.balance += payment_data.amount

                    uow.session.add(user)
                    await uow.commit()
                    await uow.session.refresh(payment)

                return payment

            except SQLAlchemyError as e:
                await uow.rollback()
                raise HTTPException(status_code=500, detail=f"An error occurred while processing the payment: {str(e)}")

    @staticmethod
    async def get_all_payments(uow: UnitOfWork) -> list[PaymentResponse]:
        async with uow:
            payments = await uow.payments.find_all()

            # Повернення списку PaymentResponse
            return list(payments)

    @staticmethod
    async def get_payment_by_id(uow: UnitOfWork, payment_id: int) -> PaymentResponse:
        async with uow:
            # Отримання платежу за його ID, якщо не знайдено - виклик виключення
            payment = await uow.payments.find_by_id(payment_id)
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")

            # Повернення PaymentResponse
            return PaymentResponse(
                id=payment.id,
                user_id=payment.user_id,
                parking_id=payment.parking_id,
                amount=payment.amount,
                currency=payment.currency,
                payment_method=payment.payment_method,
                is_successful=payment.is_successful,
                payment_date=payment.payment_date
            )

    @staticmethod
    async def delete_payment(uow: UnitOfWork, payment_id: int) -> None:
        async with uow:
            # Отримання платежу для видалення
            payment = await PaymentsService.get_payment_by_id(uow, payment_id)
            try:
                await uow.session.delete(payment)
                await uow.commit()
            except SQLAlchemyError:
                # Відкат транзакції у випадку помилки
                await uow.rollback()
                raise HTTPException(status_code=500, detail="An error occurred while deleting the payment")
