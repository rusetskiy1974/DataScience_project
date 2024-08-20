from fastapi import HTTPException, status

from app.schemas.users import UserSchemaAdd, UserResponse
from app.utils.unitofwork import IUnitOfWork


class UsersService:
    async def add_user(self, uow: IUnitOfWork, user: UserSchemaAdd):
        user_dict = user.model_dump()
        async with uow:
            if await uow.users.find_one_or_none(email=user_dict["email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists."
                )
            user_id = await uow.users.add_one(user_dict)
            return user_id

    async def get_users(self, uow: IUnitOfWork):
        async with uow:
            users = await uow.users.find_all()
            return users

    async def get_user_by_id(self, uow: IUnitOfWork, user_id: int) -> UserResponse:
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user

    async def delete_user(self, uow: IUnitOfWork, user_id: int) -> UserResponse:
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            await uow.users.delete_one(id=user_id)
            return user


user_service = UsersService()
