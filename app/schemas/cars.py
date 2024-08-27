from typing import Optional

from pydantic import BaseModel, conint


class CarSchemaAdd(BaseModel):
    brand: str
    model: str
    license_plate: str
    owner_id: conint(ge=1)
    rate_id: conint(ge=1)

    class Config:
        from_attributes = True


class CarSchemaUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    license_plate: Optional[str] = None
    rate_id: Optional[int] = None

    class Config:
        from_attributes = True


class CarResponse(BaseModel):
    id: conint(ge=1)
    brand: str
    model: str
    license_plate: str
    owner_id: int
    rate_id: int

    class Config:
        from_attributes = True
