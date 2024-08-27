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
    rates = await rates_service.get_rates(uow)
    return rates


@router.get("/{rate_id}", response_model=RateResponse, status_code=status.HTTP_200_OK)
async def get_rate(
        uow: UOWDep,
        rate_id: int,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    return await rates_service.get_rate_by_id(uow, rate_id)


@router.post("/", response_model=RateResponse, status_code=status.HTTP_201_CREATED)
async def add_rate(
        uow: UOWDep,
        rate_data: RateSchemaBase,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
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
    rate = await rates_service.get_rate_by_id(uow, rate_id)
    return await rates_service.update_rate(uow, rate_id, rate_data)


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate(
        uow: UOWDep,
        rate_id: int,
        rates_service: RatesService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    await rates_service.delete_rate(uow, rate_id)
