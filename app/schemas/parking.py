from datetime import datetime

from pydantic import BaseModel, conint
from enum import Enum


class ParkingCreate(BaseModel):
    license_plate: str


class ParkingResponse(BaseModel):
    id: conint(ge=1)
    car_id: int
    license_plate: str
    is_active: bool
    start_time: datetime
    end_time: datetime | None

    class Config:
        from_attributes = True


class ParkingLiteResponse(BaseModel):
    id: conint(ge=1)
    car_id: int
    is_active: bool
    start_time: datetime
    end_time: datetime | None

    class Config:
        from_attributes = True


class ParkingPeriod(Enum):
    WEEK = "тиждень"
    MONTH = "місяць"
    YEAR = "рік"
    ALL = "вся історія парковок"
