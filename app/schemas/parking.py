from datetime import datetime

from pydantic import BaseModel


class ParkingCreate(BaseModel):
    license_plate: str


class ParkingResponse(BaseModel):
    id: int
    car_id: int
    owner_id: int
    is_active: bool
    start_time: datetime
    end_time: datetime | None
    cost: float | None

    class Config:
        from_attributes = True
