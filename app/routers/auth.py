from fastapi import APIRouter, Depends

from app.schemas.auth import TokenResponse, UserSchemaLogin
from app.schemas.users import UserSchema, UserSchemaAdd
from app.services.auth import AuthService
from app.services.users import UsersService
from app.utils.dependencies import UOWDep

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/signup", response_model=UserSchema)
async def signup(
    user: UserSchemaAdd,
    uow: UOWDep,
    user_service: UsersService = Depends(),
):
    user_id = await user_service.add_user(uow, user)
    created_user = await user_service.get_user_by_id(uow, user_id)
    return created_user


@router.post("/login", response_model=TokenResponse)
async def login(
    user: UserSchemaLogin,
    uow: UOWDep,
    auth_service: AuthService = Depends(),
):
    db_user = await auth_service.authenticate_user(uow, user.email, user.password)
    access_token = await auth_service.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
