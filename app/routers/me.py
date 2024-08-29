from fastapi import APIRouter, Depends, status
from app.models.users import User
from app.schemas.users import UserResponse, UserWithCarsResponse
from app.schemas.parking import ParkingResponse, ParkingLiteResponse
from app.schemas.payment import PaymentResponse
from app.services.users import UsersService
from app.services.cars import CarsService
from app.services.parkings import ParkingService
from app.services.payments import PaymentsService
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
    """Retrieve the details of the current user along with their cars.

    This endpoint returns information about the currently authenticated user and their associated cars.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        user_service (UsersService): Service for user-related operations.
        cars_service (CarsService): Service for car-related operations.
        current_user (User): The currently authenticated user.

    Returns:
        UserWithCarsResponse: A response object containing user details and a list of their cars.
    """
    user = await user_service.get_user_by_id(uow, current_user.id)
    cars = await cars_service.get_cars_by_owner_id(uow, current_user.id)
    return {"user": user, "cars": cars}


@router.get("/parkings", response_model=dict[str, list[ParkingLiteResponse]], status_code=status.HTTP_200_OK)
async def get_my_parkings(
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
):
    """Retrieve all parking sessions associated with the current user.

    This endpoint returns a dictionary where the key is a string identifier and the value is a list of parking sessions
    that belong to the currently authenticated user.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        parking_service (ParkingService): Service for parking-related operations.
        current_user (User): The currently authenticated user.

    Returns:
        dict[str, list[ParkingResponse]]: A dictionary containing a list of parking sessions for the user.
    """
    parkings = await parking_service.get_parkings_by_owner_id(uow, current_user.id)
    return parkings


@router.get("/payments", response_model=dict[str, list[PaymentResponse]], status_code=status.HTTP_200_OK)
async def get_my_payments(
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
):
    """Retrieve all payments made by the current user.

    This endpoint returns a dictionary where the key is a string identifier and the value is a list of payments
    made by the currently authenticated user.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        payments_service (PaymentsService): Service for payment-related operations.
        current_user (User): The currently authenticated user.

    Returns:
        dict[str, list[PaymentResponse]]: A dictionary containing a list of payments made by the user.
    """
    payments = await payments_service.get_my_payments(uow, current_user.id)
    return payments
