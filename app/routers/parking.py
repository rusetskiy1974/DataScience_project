import base64

import cv2
import numpy as np
from app.services.license_plate_detector_base import detector, recognizer
from typing import List

from fastapi import APIRouter, Depends, status, Query, UploadFile, HTTPException
from app.models.users import User
from app.schemas.parking import ParkingCreate, ParkingResponse
from app.services.parking import ParkingService
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/parking", tags=["Parking"])




@router.post("/detect")
async def plate_detector(file: UploadFile):
    try:
        # print(f"plate_recognize : {file}")
        image = await file.read()  # Read the file content as bytes

        # Завантажте зображення безпосередньо з байтів
        img_array = np.frombuffer(image, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        img = detector.resize_image(img)
        plate_img, plates = detector.detect_plate(img, "Sample Plate")
        output_list_number = set()
        # detector.display(plate_img, "Find Plate")
        detector.display(plate_img, "Find Plate")
        for plate in plates:

            chars_list = detector.segment_characters(plate)
            # if len(chars_list) > 0:
            #     # detector.display(plate, "Find Plate")
            #     # print(len(chars_list))
            #     plt.figure(figsize=(3, 1))
            #     for i in range(len(chars_list)):
            #         plt.subplot(1, 10, i + 1)
            #         plt.imshow(chars_list[i], cmap="gray")
            #         plt.axis("off")
            #
            #     plt.show()
            plate_text = recognizer.segment_characters(chars_list)
            if len(plate_text) > 6:
                output_list_number.add(plate_text)
        for rec in output_list_number:
            print(rec)
            # print(f"{result=}")
            return {"result": list(output_list_number)}
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

