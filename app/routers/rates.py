from fastapi import APIRouter, Depends, status

from app.models.users import User
from app.models.cars import Car
from app.schemas.rates import RateSchemaBase, RateSchemaUpdate, RateResponse
from app.services.auth import auth_service
from app.services.rates import RatesService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/rates", tags=["Rates"])


@router.get("/", response_model=list[RateResponse])
async def get_rates(
        uow: UOWDep,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve all rates.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        rates_service (RatesService): Service for managing rates.
        current_user (User): The current user, required for authentication.

    Returns:
        list[RateResponse]: List of all rates.
    """
    rates = await rates_service.get_rates(uow)
    return rates


@router.get("/{rate_id}", response_model=RateResponse, status_code=status.HTTP_200_OK)
async def get_rate(
        uow: UOWDep,
        rate_id: int,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a rate by its ID.

    This endpoint allows an admin user to retrieve a specific rate by its ID.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        rate_id (int): The ID of the rate to retrieve.
        rates_service (RatesService): Service for managing rates.
        current_user (User): The current user, required to be an admin.

    Returns:
        RateResponse: The rate object corresponding to the specified ID.
    """
    return await rates_service.get_rate_by_id(uow, rate_id)


@router.post("/", response_model=RateResponse, status_code=status.HTTP_201_CREATED)
async def add_rate(
        uow: UOWDep,
        rate_data: RateSchemaBase,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Add a new rate.

    This endpoint allows an admin user to add a new rate to the system.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        rate_data (RateSchemaBase): Data for creating a new rate.
        rates_service (RatesService): Service for managing rates.
        current_user (User): The current user, required to be an admin.

    Returns:
        RateResponse: The newly created rate object.
    """
    rate_id = await rates_service.add_rate(uow, rate_data)
    return await rates_service.get_rate_by_id(uow, rate_id)


@router.put("/{rate_id}", response_model=RateResponse, status_code=status.HTTP_200_OK)
async def update_rate(
        uow: UOWDep,
        rate_id: int,
        rate_data: RateSchemaUpdate,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Update an existing rate.

    This endpoint allows an admin user to update an existing rate by its ID.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        rate_id (int): The ID of the rate to update.
        rate_data (RateSchemaUpdate): The updated data for the rate.
        rates_service (RatesService): Service for managing rates.
        current_user (User): The current user, required to be an admin.

    Returns:
        RateResponse: The updated rate object.
    """
    rate = await rates_service.get_rate_by_id(uow, rate_id)
    return await rates_service.update_rate(uow, rate_id, rate_data)


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate(
        uow: UOWDep,
        rate_id: int,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Delete a rate by its ID.

    This endpoint allows an admin user to delete a specific rate by its ID.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        rate_id (int): The ID of the rate to delete.
        rates_service (RatesService): Service for managing rates.
        current_user (User): The current user, required to be an admin.

    Returns:
        None: This endpoint does not return any content upon success.
    """
    await rates_service.delete_rate(uow, rate_id)
