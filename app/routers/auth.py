from fastapi import APIRouter, Depends

from app.schemas.auth import TokenResponse, UserSchemaLogin
from app.schemas.users import UserSchema, UserSchemaAdd
from app.services.auth import AuthService
from app.services.users import UsersService
from app.utils.dependencies import UOWDep
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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







async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return email


@router.get("/protected", response_model=UserSchema)
async def protected_route(
    uow: UOWDep,
    user_service: UsersService = Depends(),
    current_user: str = Depends(get_current_user),
):
    user = await user_service.get_user_by_email(uow, current_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
