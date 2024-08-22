from fastapi import HTTPException, status
from app.utils.unitofwork import UnitOfWork
from app.schemas.cars import CarSchemaAdd, CarSchemaUpdate, CarResponse

class CarsService:
    async def add_car(self, uow: UnitOfWork, car_data: CarSchemaAdd, owner_id: int) -> int:
        car_dict = car_data.model_dump()
        car_dict["owner_id"] = owner_id

        async with uow:
            if await uow.cars.find_one_or_none(license_plate=car_dict["license_plate"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Car with this license plate already exists.",
                )
            car_id = await uow.cars.add_one(car_dict)
            return car_id

    async def get_cars(self, uow: UnitOfWork):
        async with uow:
            cars = await uow.cars.find_all()
            return cars

    async def get_car_by_id(self, uow: UnitOfWork, car_id: int) -> CarResponse:
        async with uow:
            car = await uow.cars.find_one_or_none(id=car_id)
            if car is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
                )
            return car

    async def update_car(
        self, uow: UnitOfWork, car_id: int, car_data: CarSchemaUpdate
    ) -> CarResponse:
        async with uow:
            car = await uow.cars.find_one_or_none(id=car_id)
            if car is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
                )

            for key, value in car_data.model_dump().items():
                setattr(car, key, value)

            await uow.commit()
            return CarResponse.from_orm(car)

    async def delete_car(self, uow: UnitOfWork, car_id: int) -> CarResponse:
        async with uow:
            car = await uow.cars.find_one_or_none(id=car_id)
            if car is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
                )
            await uow.cars.delete_one(id=car_id)
            return car
