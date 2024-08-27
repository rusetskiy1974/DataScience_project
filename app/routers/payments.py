from fastapi import APIRouter, Depends, status, Query  # type: ignore

from app.schemas.payment import PaymentSchemaAdd, PaymentResponse, PaymentSchema, PaymentPeriod
from app.schemas.parking import ParkingCreate

from app.services.payments import PaymentsService
from app.services.auth import auth_service
from app.utils.guard import guard
from app.utils.dependencies import UOWDep
from app.models.users import User

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=list[PaymentResponse])
async def get_payments(
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(guard.is_admin),
        period: PaymentPeriod = Query(PaymentPeriod.ALL, description="Фільтр по періоду платежів"),
):
    payments = await payments_service.get_all_payments(uow, period)
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def get_payment_by_id(
        payment_id: int,
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    # Отримання інформації про конкретний платіж за його ID
    payment = await payments_service.get_payment_by_id(uow, payment_id)
    return payment


@router.get("/license_plate/{license_plate}", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK)
async def get_payments_by_license_plate(
        license_plate: str,
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    payments = await payments_service.get_payments_by_license_plate(uow, license_plate)
    return payments


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
        payment_id: int,
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    # Видалення конкретного платежу за його ID
    await payments_service.delete_payment(uow, payment_id)
