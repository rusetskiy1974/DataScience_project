from typing import Optional

from pydantic import BaseModel, conint


class BlackListSchemaAdd(BaseModel):
    license_plate: str
    reason: str


class BlackListSchema(BaseModel):
    card_id: int
    reason: str

    class Config:
        from_attributes = True


class BlackListResponse(BaseModel):
    id: int
    car_id: int
    license_plate: str
    reason: str

    # class Config:
    #     from_attributes = True
