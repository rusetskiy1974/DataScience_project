from fastapi import APIRouter, Depends, status, Query  # type: ignore

from app.schemas.transactions import TransactionSchemaAdd, TransactionResponse
from app.services.transactions import TransactionsService
from app.services.auth import auth_service
from app.utils.guard import guard
from app.utils.dependencies import UOWDep
from app.models.users import User

router = APIRouter(prefix="/transactions", tags=["Transaction"])


@router.get("/", response_model=list[TransactionResponse])
async def get_transactions(
        uow: UOWDep,
        transactions_service: TransactionsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve all transactions.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        transactions_service (TransactionsService): Service for managing transactions.
        current_user (User): The current user, must be an admin.

    Returns:
        list[TransactionResponse]: List of transactions.
    """
    transactions = await transactions_service.get_all_transactions(uow)
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
        transaction_id: int,
        uow: UOWDep,
        transactions_service: TransactionsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a transaction by its ID.

    Args:
        transaction_id (int): ID of the transaction.
        uow (UOWDep): Dependency for the unit of work.
        transactions_service (TransactionsService): Service for managing transactions.
        current_user (User): The current user, must be an admin.

    Returns:
        TransactionResponse: Response containing transaction data.
    """
    transaction = await transactions_service.get_transaction_by_id(uow, transaction_id)
    return transaction


@router.get("/{user_id}/transactions", response_model=list[TransactionResponse])
async def get_transactions_by_user_id(
        uow: UOWDep,
        user_id: int,
        transactions_service: TransactionsService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
) -> list[TransactionResponse]:
    """Retrieve transactions by user ID.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        user_id (int): ID of the user to retrieve transactions for.
        transactions_service (TransactionsService): Service for managing transactions.
        current_user (User): The current user, required for authentication.

    Returns:
        list[TransactionResponse]: List of transactions associated with the specified user.
    """
    transactions = await transactions_service.get_transactions_by_user_id(uow, user_id)
    # transactions = await uow.transactions.find_by_user_id(user_id=user_id)
    return transactions



@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def add_transaction(
        uow: UOWDep,
        transaction_data: TransactionSchemaAdd,
        transactions_service: TransactionsService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
):
    """Add a new transaction for the current user.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        transaction_data (TransactionSchemaAdd): Data for adding a new transaction.
        transactions_service (TransactionsService): Service for managing transactions.
        current_user (User): The current user, required for authentication.

    Returns:
        TransactionResponse: Response with the newly created transaction data.
    """
    return await transactions_service.add_transaction(uow, amount = transaction_data.amount, user_id = current_user.id)


# @router.post("/", response_model=TransactionResponse)
# async def add_transaction(
#         uow: UOWDep,
#         transaction_data: TransactionSchemaAdd,
#         transactions_service: TransactionsService = Depends(),
#         current_user: User = Depends(auth_service.get_current_user),
# ):
#     transaction_id = await transactions_service.add_transaction(uow, transaction_data)
#     return await transactions_service.get_transaction_by_id(uow, transaction_id)



@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
        uow: UOWDep,
        transaction_id: int,
        transactions_service: TransactionsService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Delete a transaction by its ID.

    Args:
        transaction_id (int): ID of the transaction to delete.
        uow (UOWDep): Dependency for the unit of work.
        transactions_service (TransactionsService): Service for managing transactions.
        current_user (User): The current user, must be an admin.
    """
    await transactions_service.delete_transaction(uow, transaction_id)
