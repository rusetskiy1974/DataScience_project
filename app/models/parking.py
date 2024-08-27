from sqlalchemy import Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import Base


class Parking(Base):
    __tablename__ = "parkings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), nullable=False)
    # owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # duration: Mapped[float] = mapped_column(Float, nullable=True)
    # cost: Mapped[float] = mapped_column(Float, nullable=True)

    car = relationship("Car", back_populates="parkings", lazy="joined")
    # owner = relationship("User")
    # payment = relationship("Payment", back_populates="parking")
