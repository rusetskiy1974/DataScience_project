from fastapi import APIRouter, Depends, status

from app.models import User
from app.schemas.users import UserResponse, UserSchemaUpdate
from app.services.auth import auth_service
from app.services.users import UsersService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def get_users(
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: User = Depends(guard.is_admin),
):
    users = await user_service.get_users(uow)
    return users


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: User = Depends(guard.is_admin),
):
    return await user_service.get_user_by_id(uow, user_id)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user_data: UserSchemaUpdate,
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await user_service.update_user(uow, user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: User = Depends(guard.is_admin),
):
    await user_service.delete_user(uow, user_id)
