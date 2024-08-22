from typing import Optional

from pydantic import BaseModel


class CarSchemaAdd(BaseModel):
    brand: str
    model: str
    license_plate: str

    class Config:
        from_attributes = True


class CarSchemaUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None

    class Config:
        from_attributes = True


class CarResponse(BaseModel):
    id: int
    brand: str
    model: str
    license_plate: str
    owner_id: int

    class Config:
        from_attributes = True
