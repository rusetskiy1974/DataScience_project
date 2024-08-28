from fastapi import HTTPException, status
from sqlalchemy import func, select
from app.schemas.users import UserResponse, UserSchemaAdd, UserSchemaUpdate
from app.utils.unitofwork import UnitOfWork


class UsersService:
    """
    Service class for handling user-related operations.
    """

    async def add_user(self, uow: UnitOfWork, user: UserSchemaAdd):
        """
        Adds a new user to the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user (UserSchemaAdd): The schema containing user data to be added.

        Returns:
            int: The ID of the newly added user.

        Raises:
            HTTPException: If a user with the provided email already exists.
        """
        user_dict = user.model_dump()
        async with uow:
            count = await uow.users.count()
            if count == 0:
                user_dict["is_admin"] = True

            if await uow.users.find_one_or_none(email=user_dict["email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists.",
                )
            user_id = await uow.users.add_one(user_dict)
            return user_id

    async def get_users(self, uow: UnitOfWork):
        """
        Retrieves all users from the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            list: A list of all users.

        """
        async with uow:
            users = await uow.users.find_all()
            return users

    async def get_user_by_id(self, uow: UnitOfWork, user_id: int) -> UserResponse:
        """
        Retrieves a user by their ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user_id (int): The ID of the user to be retrieved.

        Returns:
            UserResponse: The user data.

        Raises:
            HTTPException: If the user with the specified ID is not found.
        """
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return user

    async def update_user(
        self, uow: UnitOfWork, user_id: int, user_data: UserSchemaUpdate
    ) -> UserResponse:
        """
        Updates user information.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user_id (int): The ID of the user to be updated.
            user_data (UserSchemaUpdate): The schema containing the updated user data.

        Returns:
            UserResponse: The updated user data.

        Raises:
            HTTPException: If the user with the specified ID is not found.
        """
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            for key, value in user_data.model_dump().items():
                setattr(user, key, value)

            await uow.commit()
            return UserResponse.from_orm(user)

    async def delete_user(self, uow: UnitOfWork, user_id: int) -> UserResponse:
        """
        Deletes a user by their ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user_id (int): The ID of the user to be deleted.

        Returns:
            UserResponse: The deleted user data.

        Raises:
            HTTPException: If the user with the specified ID is not found.
        """
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            await uow.users.delete_one(id=user_id)
            return user


# Instantiate the UsersService
user_service = UsersService()
