from fastapi import HTTPException, status

from app.models import Car, BlackList
from app.utils.unitofwork import UnitOfWork
from app.schemas.black_list import BlackListResponse, BlackListSchemaAdd, BlackListSchema


class BlackListService:
    @staticmethod
    async def add_black_list(uow: UnitOfWork, black_list_data: BlackListSchemaAdd) -> BlackListResponse:
        async with uow:
            car = await uow.cars.find_one_or_none(license_plate=black_list_data.license_plate)
            if car is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
            black_record = await uow.black_list.find_one_or_none(car_id=car.id)
            if black_record:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Car already blacklisted")
            black_data = BlackList(car_id=car.id, reason=black_list_data.reason)
            uow.session.add(black_data)
            await uow.commit()
            await uow.session.refresh(black_data)
            black_response = BlackListResponse(
                id=black_data.id,
                car_id=black_data.car_id,
                license_plate=black_list_data.license_plate,
                reason=black_data.reason,
           )

            return black_response

    @staticmethod
    async def get_black_list(uow: UnitOfWork):
        async with uow:
            output_data = []
            black_list = await uow.black_list.find_all()
            for record in black_list:
                car = await uow.cars.find_one(id=record.car_id)
                output_data.append(BlackListResponse(
                    id=record.id,
                    car_id=record.car_id,
                    license_plate=car.license_plate,
                    reason=record.reason,
                ))
            return output_data

    @staticmethod
    async def delete_black_list(uow: UnitOfWork, license_plate: str):
        async with uow:
            car = await uow.cars.find_one_or_none(license_plate=license_plate)
            if car is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
            black_record = await uow.black_list.find_one_or_none(car_id=car.id)
            if black_record is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not blacklisted")
            await uow.black_list.delete_one(id=black_record.id)
