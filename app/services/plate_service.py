import base64
from app.core.config import settings


def build_base64_image(binary_image_data):
    return base64.b64encode(binary_image_data).decode("utf-8")
