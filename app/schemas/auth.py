from typing import Optional

from pydantic import BaseModel, EmailStr


class UserSchemaLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = "123456"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
