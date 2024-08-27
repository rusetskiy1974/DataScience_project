from fastapi import Depends, HTTPException, status

from app.models import User, BlackList
from app.models.cars import Car
from app.services.auth import auth_service
# from app.services.parking import ParkingService
from app.utils.unitofwork import UnitOfWork
from app.core.config import settings


class Guard:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    async def is_admin(
            self, current_user: User = Depends(auth_service.get_current_user)
    ) -> User:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Administrator privileges required",
            )
        return current_user

    async def is_owner(self, user: User, car: Car):
        if car.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )
        return True
    @staticmethod
    async def blacklisted(uow: UnitOfWork, car_id: int) -> bool:
        async with uow:
            car = await uow.cars.find_one_or_none(id=car_id)
            if car is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

            car_in_blacklist = await uow.black_list.find_one_or_none(car_id=car.id)
            if car_in_blacklist:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your car is blacklisted. Please contact the administrator."
                )
            return True

    @staticmethod
    async def car_exists(uow: UnitOfWork, car_id: int):
        async with uow:
            car = await uow.cars.find_one_or_none(id=car_id)
            if not car:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Car not found. Please register your car before starting parking."
                )
        return True

    @staticmethod
    def positive_balance(user: User) -> None:  # parking_service: ParkingService) -> None:
        if user.balance <= -settings.CREDIT_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient balance to complete the parking."
            )


guard = Guard(auth_service)
