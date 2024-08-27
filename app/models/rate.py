from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import Base


class Rate(Base):
    __tablename__ = "rates"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False)

    cars = relationship("Car", back_populates="rate")

