from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    balance: Mapped[float] = mapped_column(default=0.0)

    cars = relationship("Car", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")
    # parkings = relationship("Parking", back_populates="owner")
    # payment = relationship("Payment", back_populates="user")
