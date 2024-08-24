from datetime import datetime
from pydantic import BaseModel
from app.models.payments import TransactionType


class PaymentSchemaAdd(BaseModel):
    user_id: int
    parking_id: int | None
    amount: float
    transaction_type: TransactionType = TransactionType.CREDIT
    description: str | None
    payment_date: datetime = datetime.now()

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    parking_id: int | None
    amount: float
    transaction_type: TransactionType
    description: str | None
    payment_date: datetime = datetime.now()

    class Config:
        from_attributes = True
