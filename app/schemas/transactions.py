from datetime import datetime
from pydantic import BaseModel, conint


class TransactionSchemaAdd(BaseModel):
    #user_id: conint(ge=1)
    amount: float

    class Config:
        from_attributes = True


# class TransactionResponse(TransactionSchemaAdd):
#     id: conint(ge=1)

class TransactionResponse(BaseModel):
    id: conint(ge=1)
    amount: float

    class Config:
        from_attributes = True

