from fastapi import APIRouter, Depends, status # type: ignore
from app.schemas.payment import PaymentSchemaAdd, PaymentResponse
from app.services.payment import PaymentsService
from app.services.auth import auth_service
from app.utils.guard import guard
from app.utils.dependencies import UOWDep
from app.models.users import User

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_credit_payment(
    payment_data: PaymentSchemaAdd,
    uow: UOWDep,
    payments_service: PaymentsService = Depends(),
    current_user: User = Depends(guard.is_admin),
):
    # Обробка створення нового платежу
    payment = await payments_service.process_payment(uow, payment_data)
    return payment


router.get("/", response_model=list[PaymentResponse])
async def get_payments(
    uow: UOWDep,
    payments_service: PaymentsService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
    successful_only: bool = False,
):
    # Получение списка платежей, с возможностью фильтрации только успешных платежей
    payments = await payments_service.get_payments(uow, successful_only)
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def get_payment_by_id(
    payment_id: int,
    uow: UOWDep,
    payments_service: PaymentsService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
    # Отримання інформації про конкретний платіж за його ID
    payment = await payments_service.get_payment_by_id(uow, payment_id)
    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    uow: UOWDep,
    payments_service: PaymentsService = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
):
    # Видалення конкретного платежу за його ID
    await payments_service.delete_payment(uow, payment_id)