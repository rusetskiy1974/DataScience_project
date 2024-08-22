from datetime import datetime
from pydantic import BaseModel


# Схема для створення нового платежу
class PaymentSchemaAdd(BaseModel):
    parking_id: int
    amount: float
    currency: str
    payment_method: str

    class Config:
        from_attributes = True


# Схема для відповіді з інформацією про платіж
class PaymentResponse(BaseModel):
    id: int
    user_id: int
    parking_id: int
    amount: float
    currency: str
    payment_method: str
    is_successful: bool
    payment_date: datetime

    class Config:
        from_attributes = True
