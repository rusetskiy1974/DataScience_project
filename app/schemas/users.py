import logging
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, conint
from pydantic_core.core_schema import ValidationInfo

from app.schemas.cars import CarResponse
from app.services.auth import auth_service


class UserSchema(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserSchemaAdd(BaseModel):
    name: str
    email: EmailStr
    password1: Optional[str] = "123456"
    password2: Optional[str] = "123456"

    @field_validator("password2")
    def passwords_match(cls, value: str, values: ValidationInfo) -> str:
        if "password1" in values.data and value != values.data["password1"]:
            logging.error("Passwords do not match")
            raise ValueError("Passwords do not match")
        return value

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data["hashed_password"] = auth_service.get_password_hash(data.pop("password1"))
        data.pop("password2", None)
        return data


class UserResponse(BaseModel):
    id: conint(ge=1)
    name: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    balance: float

    class Config:
        from_attributes = True


class UserWithCarsResponse(BaseModel):
    user: UserResponse
    cars: list[CarResponse]

    class Config:
        from_attributes = True


class UserSchemaUpdate(BaseModel):
    name: str
    password1: Optional[str] = "123456"
    password2: Optional[str] = "123456"

    @field_validator("password2")
    def passwords_match(cls, value: str, values: ValidationInfo) -> str:
        if "password1" in values.data and value != values.data["password1"]:
            logging.error("Passwords do not match")
            raise ValueError("Passwords do not match")
        return value

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data["hashed_password"] = auth_service.get_password_hash(data.pop("password1"))
        data.pop("password2", None)
        return data
