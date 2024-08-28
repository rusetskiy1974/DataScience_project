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
    """
    Service class for managing payments, including calculating costs and processing payments.
    """
    @staticmethod
    async def calculate_cost(parking: Parking) -> float | None:
        """
        Calculates the parking cost based on the duration and hourly rate of the car.

        Args:
            parking (Parking): The parking instance containing start and end time.

        Returns:
            float | None: The calculated cost or None if the end time is not set.
        """
        if parking.end_time:
            duration_hours = math.ceil((parking.end_time - parking.start_time).total_seconds() / 3600)
            return duration_hours * parking.car.rate.hourly_rate
        return None

    @staticmethod
    async def process_payment(uow: UnitOfWork, parking_id: int) -> int:
        """
        Processes a payment for a parking session.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            parking_id (int): The ID of the parking session to process payment for.

        Returns:
            int: The ID of the created payment.

        Raises:
            HTTPException: If the car or user is not found, or if there is an error during payment processing.
        """
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
        """
        Retrieves all payments for a specified period.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            period (PaymentPeriod): The period for which to retrieve payments.

        Returns:
            list[PaymentResponse]: A list of payments for the specified period.
        """
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
        """
        Retrieves a specific payment by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            payment_id (int): The ID of the payment to retrieve.

        Returns:
            PaymentResponse: The payment data.

        Raises:
            HTTPException: If the payment with the specified ID is not found.
        """
        async with uow:
            # Отримання платежу за його ID, якщо не знайдено - виклик виключення
            payment = await uow.payments.find_by_payment_id(payment_id)
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")

            # Повернення PaymentResponse
            return payment

    @staticmethod
    async def get_payments_by_license_plate(uow: UnitOfWork, license_plate: str) -> list[PaymentResponse]:
        """
        Retrieves payments for a specific car license plate.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            license_plate (str): The license plate of the car.

        Returns:
            list[PaymentResponse]: A list of payments associated with the specified license plate.
        """
        async with uow:
            payments = await uow.payments.find_by_license_plate(license_plate)

            return payments

    @staticmethod
    async def get_my_payments(uow: UnitOfWork, user_id: int) -> dict[str, list[PaymentResponse]]:
        """
        Retrieves all payments made by the user, grouped by car license plate.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user_id (int): The ID of the user whose payments to retrieve.

        Returns:
            dict[str, list[PaymentResponse]]: A dictionary where keys are license plates and values are lists of payments.
        """
        async with uow:
            payments_by_car_id = {}
            cars = await uow.cars.find_by_owner_id(user_id)
            for car in cars:
                payments = await uow.payments.find_by_car_id(car.id)
                payments_by_car_id[car.license_plate] = list(payments)

            return payments_by_car_id

    @staticmethod
    async def delete_payment(uow: UnitOfWork, payment_id: int) -> None:
        """
        Deletes a payment by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            payment_id (int): The ID of the payment to delete.

        Raises:
            HTTPException: If there is an error during the deletion process.
        """
        async with uow:
            payment = await uow.payments.find_by_payment_id(payment_id)
            try:
                await uow.session.delete(payment)
                await uow.commit()
            except SQLAlchemyError:
                # Відкат транзакції у випадку помилки
                await uow.rollback()
                raise HTTPException(status_code=500, detail="An error occurred while deleting the payment")
