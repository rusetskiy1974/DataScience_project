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
        current_user: User = Depends(guard.is_admin),):
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
        current_user: User = Depends(guard.is_admin),
        # car: Car = Depends(guard.blacklisted),
):
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
    parkings = await parking_service.get_parkings(uow, period, active_only=active_only)
    return parkings


@router.put("/{parking_id}/complete", response_model=ParkingResponse, status_code=status.HTTP_200_OK)
async def complete_parking_by_id(
        license_plate: str,
        uow: UOWDep,
        parking_service: ParkingService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    parking = await parking_service.complete_parking(uow, license_plate=license_plate)
    return parking
