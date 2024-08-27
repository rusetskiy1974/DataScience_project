from datetime import datetime
from pydantic import BaseModel, conint
from app.models.payments import TransactionType
from enum import Enum


class PaymentSchemaAdd(BaseModel):
    user_id: int
    parking_id: int | None = None
    amount: float
    transaction_type: TransactionType = TransactionType.CREDIT
    description: str | None = None
    payment_date: datetime = datetime.now()

    class Config:
        from_attributes = True


class PaymentSchema(BaseModel):
    car_id: int
    parking_id: int
    amount: float
    payment_date: datetime = datetime.now()
    description: str | None = None

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: conint(ge=1)
    car_id: int
    parking_id: int | None
    amount: float
    payment_date: datetime = datetime.now()
    description: str | None

    class Config:
        from_attributes = True


class PaymentPeriod(Enum):
    WEEK = "тиждень"
    MONTH = "місяць"
    YEAR = "рік"
    ALL = "вся історія платежів"
