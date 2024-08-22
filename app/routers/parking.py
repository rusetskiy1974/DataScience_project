import base64

import cv2
import numpy as np
from app.services.license_plate_detector_base import detector, recognizer
from typing import List

from fastapi import APIRouter, Depends, status, Query, UploadFile, HTTPException, File
from app.models.users import User
from app.schemas.parking import ParkingCreate, ParkingResponse
from app.services.parking import ParkingService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.post("/detector")
async def plate_detector(file: UploadFile = File(...)):
    try:
        image = await file.read()
        img_array = np.frombuffer(image, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return detector.load_and_detect(img, "Sample Plate")
    except Exception as e:
        print({str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


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
