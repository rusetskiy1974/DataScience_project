from fastapi import APIRouter, Depends, status

from app.models.users import User
from app.models.cars import Car
from app.schemas.cars import CarSchemaAdd, CarSchemaUpdate, CarResponse
from app.services.cars import CarsService
from app.services.auth import auth_service
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.get("/", response_model=list[CarResponse])
async def get_cars(
        uow: UOWDep,
        cars_service: CarsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a list of all cars.

    This endpoint returns a list of all cars from the database. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        list[CarResponse]: A list of car objects with details.
    """
    cars = await cars_service.get_cars(uow)
    return cars


@router.get("/{car_id}", response_model=CarResponse, status_code=status.HTTP_200_OK)
async def get_car(
        car_id: int,
        uow: UOWDep,
        cars_service: CarsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a specific car by its ID.

    This endpoint returns details of a car identified by its unique ID. Access is restricted to admin users only.

    Args:
        car_id (int): The ID of the car to retrieve.
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CarResponse: Details of the car with the specified ID.
    """
    return await cars_service.get_car_by_id(uow, car_id)


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def add_car(
        uow: UOWDep,
        car_data: CarSchemaAdd,
        cars_service: CarsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Add a new car to the database.

    This endpoint adds a new car based on the provided data and returns the details of the newly created car. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        car_data (CarSchemaAdd): Data required to create a new car.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CarResponse: Details of the newly created car.
    """
    car_id = await cars_service.add_car(uow, car_data)
    return await cars_service.get_car_by_id(uow, car_id)


@router.put("/{car_id}", response_model=CarResponse, status_code=status.HTTP_200_OK)
async def update_car(
        car_id: int,
        car_data: CarSchemaUpdate,
        uow: UOWDep,
        cars_service: CarsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Update details of an existing car.

    This endpoint updates the details of a car identified by its ID. Access is restricted to admin users only. The current user must be the owner of the car.

    Args:
        car_id (int): The ID of the car to update.
        car_data (CarSchemaUpdate): Updated data for the car.
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CarResponse: Details of the updated car.
    """
    car = await cars_service.get_car_by_id(uow, car_id)
    await guard.is_owner(current_user, car)
    return await cars_service.update_car(uow, car_id, car_data)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
        car_id: int,
        uow: UOWDep,
        cars_service: CarsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Delete a car by its ID.

    This endpoint deletes a car identified by its ID from the database. Access is restricted to admin users only.

    Args:
        car_id (int): The ID of the car to delete.
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        None: No content is returned upon successful deletion.
    """
    await cars_service.delete_car(uow, car_id)
