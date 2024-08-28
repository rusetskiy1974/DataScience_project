from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.users import User
from app.utils.unitofwork import IUnitOfWork, UnitOfWork


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM

    token_auth_scheme = HTTPBearer()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if the plain password matches the hashed password.

        Args:
            plain_password (str): The plain text password.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generate a hashed version of the password.

        Args:
            password (str): The plain text password.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_user(self, uow: IUnitOfWork, **data) -> User:
        """
        Create a new user in the database.

        Args:
            uow (IUnitOfWork): The unit of work instance for database transactions.
            **data**: The user data for the new user.

        Returns:
            User: The newly created user.

        Raises:
            HTTPException: If the user already exists.
        """
        async with uow:
            try:
                new_user = await uow.users.add_one(data)
                return new_user
            except IntegrityError as e:
                if "duplicate" in str(e.orig):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Account already exists",
                    )
                raise e

    async def authenticate_user(
        self, uow: IUnitOfWork, email: str, password: str
    ) -> User:
        """
        Authenticate a user by their email and password.

        Args:
            uow (IUnitOfWork): The unit of work instance for database transactions.
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            User: The authenticated user.

        Raises:
            HTTPException: If the credentials are invalid.
        """
        async with uow:
            user = await uow.users.find_one_or_none(email=email)
            if user is None or not self.verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
            return user

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data (dict): The data to include in the token.
            expires_delta (Optional[float]): The expiration time in seconds.

        Returns:
            str: The encoded JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def get_current_user(
        self,
        token: str = Depends(token_auth_scheme),
        uow: UnitOfWork = Depends(UnitOfWork),
    ) -> User:
        """
        Retrieve the current user based on the provided JWT token.

        Args:
            token (str): The JWT token from the request.
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            User: The currently authenticated user.

        Raises:
            HTTPException: If the token is invalid or the user is not found.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token.credentials, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        async with uow:
            user = await uow.users.find_one_or_none(email=email)
            if user is None:
                raise credentials_exception
            return user

    async def decode_token(self, token: str) -> dict:
        """
        Decode a JWT token without verifying its validity.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded token payload.

        Raises:
            HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )


auth_service = AuthService()
