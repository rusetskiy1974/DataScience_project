from fastapi import HTTPException, status
from app.utils.unitofwork import UnitOfWork
from app.schemas.rates import RateResponse, RateSchemaBase, RateSchemaUpdate


class RatesService:
    """
    Service class for managing rates, including CRUD operations.
    """

    async def add_rate(self, uow: UnitOfWork, rate_data: RateSchemaBase) -> int:
        """
        Adds a new rate to the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            rate_data (RateSchemaBase): The data for the new rate.

        Returns:
            int: The ID of the newly created rate.

        Raises:
            HTTPException: If a rate with the same name already exists.
        """
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
        """
        Retrieves all rates from the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            list[RateResponse]: A list of all rates.
        """
        async with uow:
            rates = await uow.rates.find_all()
            return rates

    async def get_rate_by_id(self, uow: UnitOfWork, rate_id: int) -> RateResponse:
        """
        Retrieves a specific rate by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            rate_id (int): The ID of the rate to be retrieved.

        Returns:
            RateResponse: The rate data.

        Raises:
            HTTPException: If the rate with the specified ID is not found.
        """
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
        """
        Updates an existing rate.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            rate_id (int): The ID of the rate to be updated.
            rate_data (RateSchemaUpdate): The new data for the rate.

        Returns:
            RateResponse: The updated rate data.

        Raises:
            HTTPException: If the rate with the specified ID is not found.
        """
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
        """
        Deletes a rate from the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            rate_id (int): The ID of the rate to be deleted.

        Returns:
            RateResponse: The deleted rate data.

        Raises:
            HTTPException: If the rate with the specified ID is not found.
        """
        async with uow:
            rate = await uow.rates.find_one_or_none(id=rate_id)
            if rate is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found"
                )
            await uow.rates.delete_one(id=rate_id)
            return rate


