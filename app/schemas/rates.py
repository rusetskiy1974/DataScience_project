from typing import Optional

from pydantic import BaseModel, conint


class RateSchemaBase(BaseModel):
    name: str
    hourly_rate: float

    class Config:
        from_attributes = True


class RateSchemaUpdate(RateSchemaBase):
    pass


class RateResponse(RateSchemaBase):
    id: conint(ge=1)

