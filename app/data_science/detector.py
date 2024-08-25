import cv2
import numpy as np
from fastapi import HTTPException

from app.data_science.character_recogniser import character_recognizer
from app.data_science.license_plate_detector import plate_detector


def detector(img):
    img_array = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not load image. Please verify the path.")
    plate = plate_detector.detect_plate(img)
    chars_list = plate_detector.segment_characters(plate)
    plate_text = character_recognizer.segment_characters(chars_list)
    return plate_text
