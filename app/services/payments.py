import math
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.models import Parking, Car
from app.models.payments import Payment
from app.schemas.payment import PaymentSchemaAdd, PaymentResponse, PaymentSchema, PaymentPeriod
from app.utils.dependencies import UnitOfWork
from app.models.payments import TransactionType
from app.utils.guard import guard


class PaymentsService:
    @staticmethod
    async def calculate_cost(parking: Parking) -> float | None:
        if parking.end_time:
            duration_hours = math.ceil((parking.end_time - parking.start_time).total_seconds() / 3600)
            return duration_hours * parking.car.rate.hourly_rate
        return None

    @staticmethod
    async def process_payment(uow: UnitOfWork, parking_id: int) -> int:
        async with (uow):
            parking = await uow.parkings.find_one_or_none(id=parking_id)

            car = await uow.cars.find_one_or_none(id=parking.car_id)
            if not car:
                raise HTTPException(status_code=404, detail="Car not found")
            user = await uow.users.find_one(id=parking.car.owner_id)
            if not user:
                raise HTTPException(status_code=404, detail="Owner not found")

            cost = await PaymentsService.calculate_cost(parking)
            if cost is None:
                raise HTTPException(status_code=400, detail="Parking duration is not valid")
            user.balance -= cost
            payment = Payment(
                car_id=parking.car_id,
                parking_id=parking.id,
                amount=cost,
                payment_date=datetime.now(),
                description=f'Parking fee for {parking.start_time.strftime("%Y-%m-%d %H:%M:%S")} - {parking.end_time.strftime("%Y-%m-%d %H:%M:%S")}',

            )

            try:
                uow.session.add(payment)
                uow.session.add(user)
                await uow.commit()
                return payment.id

            except SQLAlchemyError as e:
                await uow.rollback()
                raise HTTPException(status_code=500, detail=f"An error occurred while processing the payment: {str(e)}")

    @staticmethod
    async def get_all_payments(uow: UnitOfWork, period: PaymentPeriod) -> list[PaymentResponse]:
        async with uow:
            # Отримання списку платежів за вказаний період
            if period == PaymentPeriod.ALL:
                payments = await uow.payments.find_all()
            else:
                start_date = datetime.now()
                if period == PaymentPeriod.WEEK:
                    start_date -= timedelta(weeks=1)
                elif period == PaymentPeriod.MONTH:
                    start_date -= timedelta(days=30)
                elif period == PaymentPeriod.YEAR:
                    start_date -= timedelta(days=365)

                payments = await uow.payments.find_by_period(start_date)

            # Повернення списку PaymentResponse
            return list(payments)

    @staticmethod
    async def get_payment_by_id(uow: UnitOfWork, payment_id: int) -> PaymentResponse:
        async with uow:
            # Отримання платежу за його ID, якщо не знайдено - виклик виключення
            payment = await uow.payments.find_by_payment_id(payment_id)
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")

            # Повернення PaymentResponse
            return payment

    @staticmethod
    async def get_payments_by_license_plate(uow: UnitOfWork, license_plate: str) -> list[PaymentResponse]:
        async with uow:
            payments = await uow.payments.find_by_license_plate(license_plate)

            return payments

    @staticmethod
    async def get_my_payments(uow: UnitOfWork, user_id: int) -> dict[str, list[PaymentResponse]]:
        async with uow:
            payments_by_car_id = {}
            cars = await uow.cars.find_by_owner_id(user_id)
            for car in cars:
                payments = await uow.payments.find_by_car_id(car.id)
                payments_by_car_id[car.license_plate] = list(payments)

            return payments_by_car_id

    @staticmethod
    async def delete_payment(uow: UnitOfWork, payment_id: int) -> None:
        async with uow:
            payment = await uow.payments.find_by_payment_id(payment_id)
            try:
                await uow.session.delete(payment)
                await uow.commit()
            except SQLAlchemyError:
                # Відкат транзакції у випадку помилки
                await uow.rollback()
                raise HTTPException(status_code=500, detail="An error occurred while deleting the payment")
