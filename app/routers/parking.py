from typing import List

from fastapi import APIRouter, Depends, status, Query, UploadFile, HTTPException, File
from app.models.users import User
from app.schemas.parking import ParkingCreate, ParkingResponse
from app.services.auth import auth_service
from app.services.parking import ParkingService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard
from app.services.license_plate_detector_base import detector

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.post("/by_detector", response_model=ParkingResponse, status_code=status.HTTP_201_CREATED)
async def start_parking_by_detector(
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
        file: UploadFile = File(...), ):
    try:
        image = await file.read()
        license_plate_text = detector.load_and_detect(image)

    except Exception as e:
        print({str(e)})
        HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    # Пошук автомобіля за номером
    async with uow:
        car = await uow.cars.find_one_or_none(license_plate=license_plate_text)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found.")

    # Перевірка позитивного балансу у користувача
    guard.positive_balance(current_user, parking_service)

    parking = await parking_service.start_parking(uow, license_plate=license_plate_text.upper())

    return parking


@router.put("/complete_by_detector", response_model=ParkingResponse, status_code=status.HTTP_200_OK)
async def complete_parking_by_detector(
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(auth_service.get_current_user),
        file: UploadFile = File(...),
):
    try:
        image = await file.read()
        license_plate_text = detector.load_and_detect(image)

    except Exception as e:
        print({str(e)})
        HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

        # Пошук автомобіля за номером
    async with uow:
        car = await uow.cars.find_one_or_none(license_plate=license_plate_text)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found.")

        # Перевірка позитивного балансу у користувача
    guard.positive_balance(current_user, parking_service)

    parking = await parking_service.complete_parking(uow, license_plate=license_plate_text.upper())
    return parking


@router.post("/", response_model=ParkingResponse, status_code=status.HTTP_201_CREATED)
async def start_parking(
        parking_data: ParkingCreate,
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    parking = await parking_service.start_parking(uow, license_plate=parking_data.license_plate)
    return parking


@router.put("/{parking_id}/complete", response_model=ParkingResponse, status_code=status.HTTP_200_OK)
async def complete_parking(
        license_plate: str,
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    parking = await parking_service.complete_parking(uow, license_plate=license_plate)
    return parking


@router.get("/", response_model=List[ParkingResponse], status_code=status.HTTP_200_OK)
async def get_parkings(
        uow: UOWDep,
        active_only: bool = Query(False, description="Filter active parkings only"),
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    parkings = await parking_service.get_parkings(uow, active_only=active_only)
    return parkings
