from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.users import UserSchemaAdd
from app.schemas.auth import UserSchemaLogin, TokenResponse
from app.services.auth import auth_service
from app.utils.dependencies import UOWDep, UserServiceDep

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/signup", response_model=TokenResponse)
async def signup(
    user: UserSchemaAdd,
    uow: UOWDep,
    user_service: UserServiceDep
):
    user_id = await user_service.add_user(uow, user)
    access_token = await auth_service.create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login(
    user: UserSchemaLogin,
    uow: UOWDep,
    user_service: UserServiceDep
):
    db_user = await auth_service.authenticate_user(uow.session, user.email, user.password)
    access_token = await auth_service.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}