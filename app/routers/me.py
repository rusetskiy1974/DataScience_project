from fastapi import APIRouter, Depends, status
from app.models.users import User
from app.schemas.users import UserResponse, UserWithCarsResponse
from app.schemas.parking import ParkingResponse
from app.schemas.payment import PaymentResponse
from app.services.users import UsersService
from app.services.cars import CarsService
from app.services.parking import ParkingService
from app.services.payment import PaymentsService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard
from app.services.auth import auth_service

router = APIRouter(prefix="/me", tags=["Me"])


@router.get("/", response_model=UserWithCarsResponse, status_code=status.HTTP_200_OK)
async def get_me(
    uow: UOWDep,
    user_service: UsersService = Depends(),
    cars_service: CarsService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
    user = await user_service.get_user_by_id(uow, current_user.id)
    cars = await cars_service.get_cars_by_owner_id(uow, current_user.id)
    return {"user": user, "cars": cars}


@router.get("/parkings", response_model=list[ParkingResponse], status_code=status.HTTP_200_OK)
async def get_my_parkings(
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
):
    parkings = await parking_service.get_parkings_by_owner_id(uow, current_user.id)
    return parkings


@router.get("/payments", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK)
async def get_my_payments(
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
        successful_only: bool = False,
):
    payments = await payments_service.get_my_payments(uow, current_user.id, successful_only)
    return payments
