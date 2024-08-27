from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models.parking import Parking
from app.schemas.parking import ParkingResponse, ParkingPeriod
from app.schemas.payment import PaymentSchemaAdd
from app.services.payments import PaymentsService
from app.utils.guard import guard
from app.utils.unitofwork import UnitOfWork
from app.core.config import settings


class ParkingService:

    @staticmethod
    async def start_parking(uow: UnitOfWork, license_plate: str) -> Parking:        
        async with uow:
            car = await uow.cars.find_one_or_none(license_plate=license_plate)
            if car is None:
                raise HTTPException(status_code=404, detail="Car not found")
            await guard.blacklisted(uow, car.id)
            active_parking = await uow.parkings.find_one_or_none(car_id=car.id, is_active=True)
            if active_parking:
                raise HTTPException(status_code=400, detail="This car is already parked.")
            # guard.positive_balance(current_user, settings.PARKING_HOURLY_RATE)
            parking = Parking(
                car_id=car.id,                
                start_time=datetime.utcnow(),
                is_active=True,
                end_time=None,
            )

            uow.session.add(parking)

            await uow.commit()

            await uow.session.refresh(parking)

            return ParkingResponse(
                id=parking.id,
                car_id=parking.car_id,
                license_plate=license_plate,
                is_active=parking.is_active,
                start_time=parking.start_time,
                end_time=parking.end_time
            )


    @staticmethod
    async def complete_parking(uow: UnitOfWork, license_plate: str) -> Parking:
        async with uow:
            car = await uow.cars.find_one_or_none(license_plate=license_plate)
            if car is None:
                raise HTTPException(status_code=404, detail="Car not found")

            await guard.blacklisted(uow, car.id)

            parking = await uow.parkings.find_one_or_none(car_id=car.id, is_active=True)
            if parking is None:
                raise HTTPException(status_code=404, detail="No active parking found for this car")

            user = await uow.users.find_one(id=car.owner_id)
            if user is None:
                raise HTTPException(status_code=404, detail="Owner of the car not found")
            guard.positive_balance(user)
            if parking.end_time is None:
                parking.end_time = datetime.utcnow()

            parking.is_active = False

            await uow.commit()
            await uow.session.refresh(parking)

            await PaymentsService.process_payment(uow, parking.id)
            return ParkingResponse(
                id=parking.id,
                car_id=parking.car_id,
                license_plate=license_plate,
                is_active=parking.is_active,
                start_time=parking.start_time,
                end_time=parking.end_time
            )
            
    @staticmethod
    async def get_parkings(uow: UnitOfWork, period: ParkingPeriod, active_only: bool = False) -> list[Parking]:
        async with uow:
            # Отримання списку паркінгів за вказаний період
            if period == ParkingPeriod.ALL:
                parkings = await uow.parkings.find_all_parkings(active_only=active_only)
            else:
                start_date = datetime.now()
                if period == ParkingPeriod.WEEK:
                    start_date -= timedelta(weeks=1)
                elif period == ParkingPeriod.MONTH:
                    start_date -= timedelta(days=30)
                elif period == ParkingPeriod.YEAR:
                    start_date -= timedelta(days=365)

                parkings = await uow.parkings.find_by_period(start_date, active_only=active_only)

            return list(parkings)

    async def get_parkings_by_owner_id(self, uow: UnitOfWork, owner_id: int) -> dict[str, list[ParkingResponse]]:
        async with uow:
            parkings_by_owner = {}
            cars = await uow.cars.find_by_owner_id(owner_id)
            for car in cars:
                parkings = await uow.parkings.find_by_car_id(car.id)
                parkings_by_owner[car.license_plate] = list(parkings)
            # parkings = await uow.parkings.find_all(owner_id=owner_id)
            return parkings_by_owner

    # async def get_parkings_by_owner_id(self, uow: UnitOfWork, owner_id: int) -> list[Parking]:
    #     async with uow:
    #         parkings = await uow.parkings.find_by_owner_id(owner_id)
    #         return parkings
