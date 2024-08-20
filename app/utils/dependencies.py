from typing import Annotated

from fastapi import Depends

from app.services.users import UsersService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork


def get_uow() -> IUnitOfWork:
    return UnitOfWork()


def get_users_service() -> UsersService:
    return UsersService()


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
UserServiceDep = Annotated[UsersService, Depends(get_users_service)]
