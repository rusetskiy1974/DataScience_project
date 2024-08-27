from abc import ABC, abstractmethod

from app.db.database import async_session
from app.repositories.cars import CarsRepository
from app.repositories.parkings import ParkingRepository
from app.repositories.users import UsersRepository
from app.repositories.payments import PaymentRepository
from app.repositories.rates import RateRepository
from app.repositories.black_list import BlackListRepository
from app.repositories.transactions import TransactionRepository


class AuthRepository:
    pass


class IUnitOfWork(ABC):
    users: UsersRepository
    cars: CarsRepository
    parkings: ParkingRepository
    payments: PaymentRepository
    rates: RateRepository
    black_list: BlackListRepository
    transactions: TransactionRepository

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.cars = CarsRepository(self.session)
        self.parkings = ParkingRepository(self.session)
        self.payments = PaymentRepository(self.session)
        self.rates = RateRepository(self.session)
        self.black_list = BlackListRepository(self.session)
        self.transactions = TransactionRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
