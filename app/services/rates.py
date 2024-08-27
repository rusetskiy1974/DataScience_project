from fastapi import HTTPException, status
from app.utils.unitofwork import UnitOfWork
from app.schemas.rates import RateResponse, RateSchemaBase, RateSchemaUpdate


class RatesService:
    async def add_rate(self, uow: UnitOfWork, rate_data: RateSchemaBase) -> int:
        rate_dict = rate_data.model_dump()
        async with uow:
            if await uow.rates.find_one_or_none(name=rate_dict["name"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rate with this name already exists.",
                )
            rate_id = await uow.rates.add_one(rate_dict)
            return rate_id

    async def get_rates(self, uow: UnitOfWork):
        async with uow:
            rates = await uow.rates.find_all()
            return rates

    async def get_rate_by_id(self, uow: UnitOfWork, rate_id: int) -> RateResponse:
        async with uow:
            rate = await uow.rates.find_one_or_none(id=rate_id)
            if rate is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found"
                )
            return rate

    async def update_rate(
            self, uow: UnitOfWork, rate_id: int, rate_data: RateSchemaUpdate
    ) -> RateResponse:
        async with uow:
            rate = await uow.rates.find_one_or_none(id=rate_id)
            if rate is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found"
                )

            for key, value in rate_data.model_dump().items():
                setattr(rate, key, value)

            await uow.commit()
            return RateResponse.from_orm(rate)

    async def delete_rate(self, uow: UnitOfWork, rate_id: int) -> RateResponse:
        async with uow:
            rate = await uow.rates.find_one_or_none(id=rate_id)
            if rate is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found"
                )
            await uow.rates.delete_one(id=rate_id)
            return rate


