import cv2
from matplotlib import pyplot as plt

from app.services import license_plate_detector_base as base_detector


def main():
    # Створюємо екземпляр класу LicensePlateDetector
    detector = base_detector.LicensePlateDetector()

    # Завантажуємо зображення з диску
    image_path = "data/bmv.jpg"
    image = cv2.imread(image_path)  # Завантажуємо зображення

    # Перевіряємо, чи зображення було завантажено успішно
    if image is None:
        print(
            "Помилка: не вдалося завантажити зображення. Перевірте правильність шляху."
        )
    else:
        # Виконуємо детекцію номерного знака
        plate_img, plate = detector.detect_plate(image, "Sample Plate")
        chars_list = detector.segment_characters(plate)

        # Відображаємо зображення з детекцією
        detector.display(plate_img, "Find Plate")
        detector.display(plate, "Detected Plate")
        print(len(chars_list))
        plt.figure(figsize=(3, 1))
        for i in range(len(chars_list)):
            plt.subplot(1, 10, i + 1)
            plt.imshow(chars_list[i], cmap="gray")
            plt.axis("off")

        plt.show()


if __name__ == "__main__":
    main()
