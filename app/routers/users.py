from fastapi import APIRouter, status

from app.utils.dependencies import UOWDep
from app.schemas.users import UserSchemaAdd, UserResponse
from app.services.users import user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/add", response_model=UserResponse)
async def add_user(
    user: UserSchemaAdd,
    uow: UOWDep,
):
    user_id = await user_service.add_user(uow, user)
    added_user = await uow.users.find_one(id=user_id)

    return added_user


@router.get("/", response_model=list[UserResponse])
async def get_users(
    uow: UOWDep,
):
    users = await user_service.get_users(uow)
    return users


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    uow: UOWDep,
):
    return await user_service.get_user_by_id(uow, user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    uow: UOWDep,
):
    await user_service.delete_user(uow, user_id)
