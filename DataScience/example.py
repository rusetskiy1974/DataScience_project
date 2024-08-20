import cv2
from matplotlib import pyplot as plt

from app.services.license_plate_detector_base import LicensePlateDetector
from app.services.license_plate_detector_base import CharacterRecognizer
from app.services.license_plate_detector_base import AutoDetector


def main():
    image_path = "data/bmv_.png"
    # Створюємо екземпляр класу LicensePlateDetector
    auto_detector = AutoDetector()
    if auto_detector.predict_image(image_path) is False:
        return
    detector = LicensePlateDetector()
    segment = CharacterRecognizer()

    # Завантажуємо зображення з диску
    # image_path = "data/photo1.jpg"
    image = cv2.imread(image_path)  # Завантажуємо зображення
    output_list_number = set()
    # Перевіряємо, чи зображення було завантажено успішно
    if image is None:
        print(
            "Помилка: не вдалося завантажити зображення. Перевірте правильність шляху."
        )
    else:
        # Виконуємо детекцію номерного знака
        image = detector.resize_image(image)
        plate_img, plates = detector.detect_plate(image, "Sample Plate")
        # Відображаємо зображення з детекцією
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
            plate_text = segment.segment_characters(chars_list)
            if len(plate_text) > 6:
                output_list_number.add(plate_text)
    for rec in output_list_number:
        print(rec)


if __name__ == "__main__":
    main()
