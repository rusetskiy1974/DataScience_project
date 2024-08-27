from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.utils.repositories import SQLAlchemyRepository
from app.models.payments import Payment
from app.models.parking import Parking
from app.models.cars import Car
from pathlib import Path

from datetime import datetime
import csv


class PaymentRepository(SQLAlchemyRepository):
    model = Payment

    async def find_by_user_id(self, user_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_car_id(self, car_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.car_id == car_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_parking_id(self, parking_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.parking_id == parking_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_payment_id(self, payment_id: int) -> Sequence[Payment]:
        stmt = select(self.model).where(self.model.id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
     

    async def find_by_license_plate(self, license_plate: str) -> list[Payment]:
        stmt = (
            select(Payment)
            .join(Car)
            .where(Car.license_plate == license_plate)
        )
        result = await self.session.execute(stmt)
        payments = result.scalars().all()

        # Prepare data for CSV
        csv_data = []
        for payment in payments:
            csv_data.append({
                'payment_id': payment.id,
                'car_id': payment.car_id,
                'parking_id': payment.parking_id,
                'amount': payment.amount,
                'payment_date': payment.payment_date.isoformat(),
                'description': payment.description,
            })
        output_directory = Path("./csv")
        output_directory.mkdir(parents=True, exist_ok=True)
        # Write to CSV file
        filename = f"{license_plate}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = output_directory / filename
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = csv_data[0].keys() if csv_data else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)
              
        return payments


    async def find_by_period(self, start_date: datetime):
        stmt = select(self.model).where(self.model.payment_date >= start_date)
        res = await self.session.execute(stmt)
        return res.scalars().all()


    async def add_one(self, payment_dict: dict) -> Payment:
        new_payment = Payment(**payment_dict)
        self.session.add(new_payment)
        await self.session.commit()
        return new_payment

