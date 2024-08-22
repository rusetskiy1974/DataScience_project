from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parking_id = Column(Integer, ForeignKey('parkings.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default='USD')  # Код валюты, например USD
    is_successful = Column(Boolean, default=False)  # Статус успешности платежа
    payment_method = Column(String, nullable=False)  # Метод оплаты, например, 'credit_card', 'paypal'
    payment_date = Column(DateTime, default=datetime.utcnow)  # Дата и время платежа

    user = relationship("User", back_populates="payments")
    parking = relationship("Parking", back_populates="payments")