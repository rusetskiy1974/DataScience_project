from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class BlackList(Base):
    __tablename__ = "black_list"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)

    car = relationship("Car")
    