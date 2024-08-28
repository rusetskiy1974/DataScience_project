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
    """Retrieve all users.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        user_service (UsersService): Service for managing users.
        current_user (User): The current user, must be an admin.

    Returns:
        list[UserResponse]: List of users.
    """
    users = await user_service.get_users(uow)
    return users


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: User = Depends(guard.is_admin),
):
    """Retrieve a user by their ID.

    Args:
        user_id (int): ID of the user.
        uow (UOWDep): Dependency for the unit of work.
        user_service (UsersService): Service for managing users.
        current_user (User): The current user, must be an admin.

    Returns:
        UserResponse: Response containing user data.
    """
    return await user_service.get_user_by_id(uow, user_id)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_data: UserSchemaUpdate,
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
    """Update a user.

    Args:
        user_data (UserSchemaUpdate): Data for updating the user.
        uow (UOWDep): Dependency for the unit of work.
        user_service (UsersService): Service for managing users.
        current_user (User): The current user.

    Returns:
        UserResponse: Response with updated user data.
    """
    return await user_service.update_user(uow, current_user.id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: User = Depends(guard.is_admin),
):
    """Delete a user by their ID.

    Args:
        user_id (int): ID of the user.
        uow (UOWDep): Dependency for the unit of work.
        user_service (UsersService): Service for managing users.
        current_user (User): The current user, must be an admin.
    """
    await user_service.delete_user(uow, user_id)
