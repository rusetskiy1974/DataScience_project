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
    cars = await cars_service.get_cars(uow)
    return cars


@router.get("/{car_id}", response_model=CarResponse, status_code=status.HTTP_200_OK)
async def get_car(
    car_id: int,
    uow: UOWDep,
    cars_service: CarsService = Depends(),
    current_user: User = Depends(guard.is_admin),
):
    return await cars_service.get_car_by_id(uow, car_id)


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def add_car(
    car_data: CarSchemaAdd,
    uow: UOWDep,
    cars_service: CarsService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
    car_id = await cars_service.add_car(uow, car_data, current_user.id)
    return await cars_service.get_car_by_id(uow, car_id)


@router.put("/{car_id}", response_model=CarResponse, status_code=status.HTTP_200_OK)
async def update_car(
    car_id: int,
    car_data: CarSchemaUpdate,
    uow: UOWDep,
    cars_service: CarsService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
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
    await cars_service.delete_car(uow, car_id)
