import enum
from sqlalchemy import Float, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.models.base import Base


class TransactionType(enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), nullable=False)
    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parking_id: Mapped[int] = mapped_column(ForeignKey("parkings.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    # paid_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # user = relationship("User", back_populates="payment")
    car = relationship("Car")
    parking = relationship("Parking")
