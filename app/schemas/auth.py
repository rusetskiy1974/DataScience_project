from pydantic import BaseModel, EmailStr


class UserSchemaLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
