from typing import List

from fastapi import APIRouter, Depends, status, Query, UploadFile, HTTPException, File

from app.models import Car
from app.models.users import User
from app.schemas.parking import ParkingCreate, ParkingResponse, ParkingPeriod
from app.services.parkings import ParkingService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard
from app.data_science.detector import detector

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.post("/by_detector", response_model=ParkingResponse, status_code=status.HTTP_201_CREATED)
async def start_parking_by_detector(
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        file: UploadFile = File(...), 
        ):
    """Start a parking session using an image detected license plate.

    This endpoint allows a user to start a parking session by uploading an image. The license plate is detected from the image.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        parking_service (ParkingService): Service for managing parking operations.
        file (UploadFile): The image file to process for license plate detection.

    Returns:
        ParkingResponse: The details of the parking session that was started.

    Raises:
        HTTPException: If there is an error processing the image, a 404 error is raised with a message.
    """
    try:
        image = await file.read()
        license_plate_text = detector(image)

    except Exception as e:
        print({str(e)})
        raise HTTPException(status_code=404, detail=f"Error processing image: {str(e)}")

    # guard.positive_balance(current_user, parking_service)

    parking = await parking_service.start_parking(uow, license_plate=license_plate_text.upper())

    return parking


@router.put("/complete_by_detector", response_model=ParkingResponse, status_code=status.HTTP_200_OK)
async def complete_parking_by_detector(
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        file: UploadFile = File(...),        
        # car: Car = Depends(guard.blacklisted),
):
    """Complete a parking session using an image detected license plate.

    This endpoint allows a user to complete a parking session by uploading an image. The license plate is detected from the image.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        parking_service (ParkingService): Service for managing parking operations.
        file (UploadFile): The image file to process for license plate detection.

    Returns:
        ParkingResponse: The details of the parking session that was completed.

    Raises:
        HTTPException: If there is an error processing the image, a 404 error is raised with a message.
    """
    try:
        image = await file.read()
        license_plate_text = detector(image)
        print("license_plate_text= ", license_plate_text)
    except Exception as e:
        print({str(e)})
        raise HTTPException(status_code=404, detail=f"Error processing image: {str(e)}")

    parking = await parking_service.complete_parking(uow, license_plate=license_plate_text.upper())
    return parking


@router.post("/", response_model=ParkingResponse, status_code=status.HTTP_201_CREATED)
async def start_parking(
        parking_data: ParkingCreate,
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(guard.is_admin),
        ):
    """Start a parking session with the provided license plate.

    This endpoint allows an admin user to start a parking session by providing a license plate.

    Args:
        parking_data (ParkingCreate): Data containing the license plate to start the parking session.
        uow (UOWDep): Dependency for the unit of work.
        parking_service (ParkingService): Service for managing parking operations.
        current_user (User): The current user, required to be an admin.

    Returns:
        ParkingResponse: The details of the parking session that was started.
    """
    parking = await parking_service.start_parking(uow, license_plate=parking_data.license_plate)
    return parking


@router.get("/", response_model=List[ParkingResponse], status_code=status.HTTP_200_OK)
async def get_parkings(
        uow: UOWDep,
        active_only: bool = Query(False, description="Filter active parkings only"),
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(guard.is_admin),
        period: ParkingPeriod = Query(ParkingPeriod.ALL, description="Фільтр по періоду паркінгів"),
):
    """Retrieve a list of parking sessions.

    This endpoint allows an admin user to retrieve a list of parking sessions, optionally filtered by period and activity status.

    Args:
        uow (UOWDep): Dependency for the unit of work.
        active_only (bool): Optional filter to include only active parking sessions.
        parking_service (ParkingService): Service for managing parking operations.
        current_user (User): The current user, required to be an admin.
        period (ParkingPeriod): Optional filter to specify the parking period.

    Returns:
        List[ParkingResponse]: A list of parking session objects matching the filters.
    """
    parkings = await parking_service.get_parkings(uow, period, active_only=active_only)
    return parkings


@router.put("/{parking_id}/complete", response_model=ParkingResponse, status_code=status.HTTP_200_OK)
async def complete_parking_by_id(
        license_plate: str,
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Complete a parking session by its ID.

    This endpoint allows an admin user to complete a parking session by providing the parking ID.

    Args:
        parking_id (int): The ID of the parking session to complete.
        uow (UOWDep): Dependency for the unit of work.
        parking_service (ParkingService): Service for managing parking operations.
        current_user (User): The current user, required to be an admin.

    Returns:
        ParkingResponse: The details of the completed parking session.
    """
    parking = await parking_service.complete_parking(uow, license_plate=license_plate)
    return parking
