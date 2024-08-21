import base64

import cv2
import numpy as np
from fastapi import APIRouter, status, UploadFile, HTTPException
from app.services.license_plate_detector_base import detector, recognizer

router = APIRouter(
    prefix="/parking",
    tags=["PARKING"],
)




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
