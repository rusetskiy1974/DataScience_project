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
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def create_user(self, uow: IUnitOfWork, **data) -> User:
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
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )


auth_service = AuthService()
