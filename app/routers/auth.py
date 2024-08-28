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
    """Register a new user.

    This endpoint allows a new user to register by providing user details. After successful registration, the details of the created user are returned.

    Args:
        user (UserSchemaAdd): The user details required for registration, including email, password, and any other necessary information.
        uow (UOWDep): Dependency for unit of work management.
        user_service (UsersService): Service for managing user-related operations.

    Returns:
        UserSchema: Details of the newly created user.

    Raises:
        HTTPException: May raise an HTTPException if registration fails.
    """
    user_id = await user_service.add_user(uow, user)
    created_user = await user_service.get_user_by_id(uow, user_id)
    return created_user


@router.post("/login", response_model=TokenResponse)
async def login(
    user: UserSchemaLogin,
    uow: UOWDep,
    auth_service: AuthService = Depends(),
):
    """Authenticate a user and generate a token.

    This endpoint allows a user to login by providing email and password. Upon successful authentication, an access token is generated and returned.

    Args:
        user (UserSchemaLogin): The user's credentials including email and password.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (AuthService): Service for managing authentication operations.

    Returns:
        TokenResponse: Contains the access token and the token type.

    Raises:
        HTTPException: May raise an HTTPException if authentication fails.
    """
    db_user = await auth_service.authenticate_user(uow, user.email, user.password)
    access_token = await auth_service.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
