from fastapi import APIRouter, Depends, status
from app.models.users import User
from app.schemas.black_list import BlackListSchemaAdd, BlackListResponse
from app.services.black_list import BlackListService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/black_list", tags=["Black List"])


@router.get("/", response_model=list[BlackListResponse])
async def get_black_list(
        uow: UOWDep,
        black_list_service: BlackListService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve the entire blacklist.

    This endpoint returns a list of all entries in the blacklist. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        black_list_service (BlackListService): Service for managing blacklist-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        list[BlackListResponse]: A list of blacklist entries.
    """
    black_list = await black_list_service.get_black_list(uow)
    return black_list


@router.post("/", response_model=BlackListResponse, status_code=status.HTTP_200_OK)
async def add_black_list(
        uow: UOWDep,
        black_list_data: BlackListSchemaAdd,
        black_list_service: BlackListService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Add a new entry to the blacklist.

    This endpoint adds a new entry to the blacklist based on the provided data and returns the details of the newly added entry. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        black_list_data (BlackListSchemaAdd): Data required to create a new blacklist entry.
        black_list_service (BlackListService): Service for managing blacklist-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        BlackListResponse: Details of the newly added blacklist entry.
    """
    return await black_list_service.add_black_list(uow, black_list_data)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_black_list(
        uow: UOWDep,
        license_plate: str,
        black_list_service: BlackListService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Remove an entry from the blacklist.

    This endpoint deletes an entry from the blacklist based on the provided license plate. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        license_plate (str): The license plate of the entry to remove from the blacklist.
        black_list_service (BlackListService): Service for managing blacklist-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        None: No content is returned upon successful deletion.
    """
    await black_list_service.delete_black_list(uow, license_plate)
