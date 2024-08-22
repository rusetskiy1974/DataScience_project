from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    brand: Mapped[str]
    model: Mapped[str]
    license_plate: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner = relationship("User", back_populates="cars")
    parkings = relationship("Parking", back_populates="car")
