from datetime import datetime
import math
from fastapi import HTTPException, status
from app.models.parking import Parking
from app.models.payments import Payment
from app.models.users import User
from app.schemas.parking import ParkingResponse
from app.schemas.payment import PaymentSchemaAdd
from app.services.payment import PaymentsService
from app.utils.unitofwork import UnitOfWork
from app.core.config import settings


class ParkingService:

    @staticmethod
    async def calculate_cost(parking: Parking) -> float:
        if parking.end_time:
            duration_hours = math.ceil((parking.end_time - parking.start_time).total_seconds() / 3600)
            return duration_hours * settings.PARKING_HOURLY_RATE
        return None

    @staticmethod
    async def start_parking(uow: UnitOfWork, license_plate: str) -> Parking:
        async with uow:
            car = await uow.cars.find_one_or_none(license_plate=license_plate)
            if car is None:
                raise HTTPException(status_code=404, detail="Car not found")

            active_parking = await uow.parkings.find_one_or_none(car_id=car.id, is_active=True)
            if active_parking:
                raise HTTPException(status_code=400, detail="This car is already parked.")

            parking = Parking(
                car_id=car.id,
                owner_id=car.owner_id,
                start_time=datetime.utcnow(),
                is_active=True,
                end_time=None,
                cost=None
            )

            uow.session.add(parking)

            await uow.commit()

            await uow.session.refresh(parking)

            return parking

    @staticmethod
    async def complete_parking(uow: UnitOfWork, license_plate: str) -> Parking:
        async with uow:
            car = await uow.cars.find_one_or_none(license_plate=license_plate)
            if car is None:
                raise HTTPException(status_code=404, detail="Car not found")
            parking = await uow.parkings.find_one_or_none(car_id=car.id, is_active=True)
            if parking is None:
                raise HTTPException(status_code=404, detail="No active parking found for this car")

            user = await uow.users.find_one(id=car.owner_id)
            if user is None:
                raise HTTPException(status_code=404, detail="Owner of the car not found")

            if parking.end_time is None:
                parking.end_time = datetime.utcnow()

            duration = math.ceil((parking.end_time - parking.start_time).total_seconds() / 3600)

            parking.cost = duration * settings.PARKING_HOURLY_RATE

            if user.balance < parking.cost:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient balance to complete the parking. Please top up your account."
                )

            user.balance -= parking.cost
            uow.session.add(user)

            parking.is_active = False

            await uow.commit()
            await uow.session.refresh(parking)
            # await uow.session.close()

            payment_dict = PaymentSchemaAdd(
                user_id=car.owner_id,
                parking_id=parking.id,
                amount=parking.cost,
                transaction_type='debit',
                payment_date=datetime.now(),
                description=f'Parking fee for {parking.start_time.strftime("%Y-%m-%d %H:%M:%S")} - {parking.end_time.strftime("%Y-%m-%d %H:%M:%S")}',

            )

            await PaymentsService.process_payment(uow, payment_dict)
            return parking

    @staticmethod
    async def get_parkings(uow: UnitOfWork, active_only: bool = False) -> list[Parking]:
        async with uow:
            parkings = await uow.parkings.find_all_parkings(active_only=active_only)
            return parkings

    async def get_parkings_by_owner_id(self, uow: UnitOfWork, owner_id: int) -> list[ParkingResponse]:
        async with uow:
            parkings = await uow.parkings.find_all(owner_id=owner_id)
            return parkings

    async def get_parkings_by_owner_id(self, uow: UnitOfWork, owner_id: int) -> list[Parking]:
        async with uow:
            parkings = await uow.parkings.find_by_owner_id(owner_id)
            return parkings
