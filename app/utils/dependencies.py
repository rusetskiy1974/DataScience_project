from typing import Annotated

from fastapi import Depends

from app.utils.unitofwork import IUnitOfWork, UnitOfWork


def get_uow() -> IUnitOfWork:
    return UnitOfWork()


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
