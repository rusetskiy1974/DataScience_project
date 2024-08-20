import logging
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core.core_schema import ValidationInfo


class UserSchema(BaseModel):
    id: int
    name: str

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
        data["hashed_password"] = data.pop("password1")  #auth_service.get_password_hash(data.pop("password1"))
        data.pop("password2", None)
        return data


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    balance: float

    class Config:
        from_attributes = True
