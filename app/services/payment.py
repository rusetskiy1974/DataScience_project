from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.models.paymets import Payment
from app.schemas.payment import PaymentSchemaAdd, PaymentResponse
from app.utils.dependencies import UnitOfWork


class PaymentsService:

    @staticmethod
    async def process_payment(uow: UnitOfWork, payment_data: PaymentSchemaAdd, user_id: int) -> PaymentResponse:
        async with uow:
            # Перевірка, чи існує паркування
            parking = await uow.parkings.find_by_id(payment_data.parking_id)
            if not parking:
                raise HTTPException(status_code=404, detail="Parking not found")

            # Перевірка, чи достатньо у користувача коштів
            user = await uow.users.find_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if user.balance < payment_data.amount:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient balance. Please top up your account."
                )

            # Створення платежу
            payment = Payment(
                user_id=user_id,
                parking_id=payment_data.parking_id,
                amount=payment_data.amount,
                currency=payment_data.currency,
                payment_method=payment_data.payment_method,
                is_successful=True,
                payment_date=datetime.utcnow()
            )

            try:
                # Оновлення балансу користувача
                user.balance -= payment_data.amount
                uow.session.add(user)

                # Додавання платежу в базу даних
                uow.session.add(payment)

                await uow.commit()
                await uow.session.refresh(payment)

                # Повернення відповіді з інформацією про платіж
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

            except SQLAlchemyError:
                # Відкат транзакції у випадку помилки
                await uow.rollback()
                raise HTTPException(status_code=500, detail="An error occurred while processing the payment")

    @staticmethod
    async def get_payments(uow: UnitOfWork, successful_only: bool = False) -> list[PaymentResponse]:
        async with uow:
            # Отримання списку всіх платежів, з можливістю фільтрації успішних платежів
            payments = await uow.payments.find_all_payments(successful_only=successful_only)

            # Повернення списку PaymentResponse
            return [
                PaymentResponse(
                    id=payment.id,
                    user_id=payment.user_id,
                    parking_id=payment.parking_id,
                    amount=payment.amount,
                    currency=payment.currency,
                    payment_method=payment.payment_method,
                    is_successful=payment.is_successful,
                    payment_date=payment.payment_date
                )
                for payment in payments
            ]

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
