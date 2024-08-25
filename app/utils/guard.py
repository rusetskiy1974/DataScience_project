from fastapi import Depends, HTTPException, status

from app.models import User
from app.models.cars import Car
from app.services.auth import auth_service
# from app.services.parking import ParkingService
from app.utils.unitofwork import UnitOfWork


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
    def positive_balance(user: User, amount: float) -> None:  # parking_service: ParkingService) -> None:
        if user.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient balance to complete the parking."
            )


guard = Guard(auth_service)
