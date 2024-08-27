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
    black_list = await black_list_service.get_black_list(uow)
    return black_list


@router.post("/", response_model=BlackListResponse, status_code=status.HTTP_200_OK)
async def add_black_list(
        uow: UOWDep,
        black_list_data: BlackListSchemaAdd,
        black_list_service: BlackListService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    return await black_list_service.add_black_list(uow, black_list_data)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_black_list(
        uow: UOWDep,
        license_plate: str,
        black_list_service: BlackListService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    await black_list_service.delete_black_list(uow, license_plate)
