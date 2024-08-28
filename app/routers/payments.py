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
    """Retrieve all payments with an optional filter by period.

    This endpoint allows an admin user to retrieve a list of all payments, optionally filtered by a specified period.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        payments_service (PaymentsService): Service for managing payments.
        current_user (User): The current user, required to be an admin.
        period (PaymentPeriod): Optional filter to specify the payment period.

    Returns:
        list[PaymentResponse]: A list of payment objects, filtered by the specified period if provided.
    """
    payments = await payments_service.get_all_payments(uow, period)
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def get_payment_by_id(
        payment_id: int,
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a payment by its ID.

    This endpoint allows an admin user to retrieve a specific payment by its ID.

    Args:
        payment_id (int): The ID of the payment to retrieve.
        uow (UOWDep): Dependency for the unit of work.
        payments_service (PaymentsService): Service for managing payments.
        current_user (User): The current user, required to be an admin.

    Returns:
        PaymentResponse: The payment object corresponding to the specified ID.
    """
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
    """Retrieve payments associated with a specific license plate.

    This endpoint allows an admin user to retrieve a list of payments associated with a given license plate.

    Args:
        license_plate (str): The license plate associated with the payments.
        uow (UOWDep): Dependency for the unit of work.
        payments_service (PaymentsService): Service for managing payments.
        current_user (User): The current user, required to be an admin.

    Returns:
        list[PaymentResponse]: A list of payment objects associated with the specified license plate.
    """
    payments = await payments_service.get_payments_by_license_plate(uow, license_plate)
    return payments


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
        payment_id: int,
        uow: UOWDep,
        payments_service: PaymentsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Delete a payment by its ID.

    This endpoint allows an admin user to delete a specific payment by its ID.

    Args:
        payment_id (int): The ID of the payment to delete.
        uow (UOWDep): Dependency for the unit of work.
        payments_service (PaymentsService): Service for managing payments.
        current_user (User): The current user, required to be an admin.

    Returns:
        None: This endpoint does not return any content upon success.
    """
    # Видалення конкретного платежу за його ID
    await payments_service.delete_payment(uow, payment_id)
