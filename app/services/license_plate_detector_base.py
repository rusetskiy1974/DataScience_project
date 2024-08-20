import cv2
from abc import ABC
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf


class Detector(ABC):

    @staticmethod
    def display(img_, title=""):
        if img_ is None:
            print("Error: Could not load image. Please verify the path.")
            return

        img = cv2.cvtColor(img_, cv2.COLOR_BGR2RGB)
        ax = plt.subplot(111)
        ax.imshow(img)
        plt.axis("off")
        plt.title(title)
        plt.show()


class LicensePlateDetector:
    def __init__(self, cascade_path="./models/indian_license_plate.xml"):
        self.plate_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_plate(self, img, text=""):
        plate_img = img.copy()
        roi = img.copy()
        all_plates = []

        for scale in np.arange(1.05, 1.35, 0.05):
            plate_rects = self.plate_cascade.detectMultiScale(
                plate_img, scaleFactor=scale, minNeighbors=8
            )

            for x, y, w, h in plate_rects:
                plate = roi[y:y + h, x:x + w, :]
                all_plates.append(plate)
                cv2.rectangle(
                    plate_img, (x + 2, y), (x + w - 3, y + h - 5), (51, 181, 155), 3
                )

        if text != "":
            plate_img = cv2.putText(
                plate_img,
                text,
                (x - w // 2, y - h // 2),
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                0.5,
                (51, 181, 155),
                1,
                cv2.LINE_AA,
            )

        return plate_img, all_plates

    @staticmethod
    def display(img_, title=""):
        if img_ is None:
            print("Error: Could not load image. Please verify the path.")
            return

        img = cv2.cvtColor(img_, cv2.COLOR_BGR2RGB)
        ax = plt.subplot(111)
        ax.imshow(img)
        plt.axis("off")
        plt.title(title)
        plt.show()

    @staticmethod
    def find_contours(dimensions, img):
        cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        lower_width, upper_width, lower_height, upper_height = dimensions
        cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

        x_cntr_list = []
        img_res = []
        for cntr in cntrs:
            intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)
            if (
                    lower_width < intWidth < upper_width
                    and intHeight > lower_height
                    and intHeight < upper_height
            ):
                x_cntr_list.append(intX)
                char_copy = np.zeros((44, 24))
                char = img[intY: intY + intHeight, intX: intX + intWidth]
                char = cv2.resize(char, (20, 40))
                char = cv2.subtract(255, char)
                char_copy[2:42, 2:22] = char
                img_res.append(char_copy)

        indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
        img_res_copy = [img_res[idx] for idx in indices]
        img_res = np.array(img_res_copy)
        return img_res

    def segment_characters(self, image):
        img = cv2.resize(image, (333, 75))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img_binary = cv2.threshold(
            img_gray, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        img_erode = cv2.erode(img_binary, (3, 3))
        img_dilate = cv2.dilate(img_erode, (3, 3))

        LP_WIDTH = img_dilate.shape[0]
        LP_HEIGHT = img_dilate.shape[1]

        img_dilate[0:3, :] = 255
        img_dilate[:, 0:3] = 255
        img_dilate[72:75, :] = 255
        img_dilate[:, 330:333] = 255

        dimensions = [LP_WIDTH / 6, LP_WIDTH / 2, LP_HEIGHT / 10, 2 * LP_HEIGHT / 3]
        char_list = self.find_contours(dimensions, img_dilate)
        return char_list

    def load_and_detect(self, image_path, text=""):
        img = cv2.imread(image_path)
        if img is None:
            print("Error: Could not load image. Please verify the path.")
            return None, None
        plate_img, plate = self.detect_plate(img, text)
        self.display(plate_img, "Detected Plate")
        return plate_img, plate

    @staticmethod
    def resize_image(img, target_height=640):
        """
        Змінює розмір зображення до заданої висоти, зберігаючи співвідношення сторін.
        """
        # Розраховуємо співвідношення сторін
        ratio = target_height / float(img.shape[0])
        # Обчислюємо нову ширину
        target_width = int(img.shape[1] * ratio)
        # Змінюємо розмір зображення
        resized = cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_AREA)
        return resized


class AutoDetector:
    def __init__(self):
        # Завантажте TFLite модель
        self.interpreter = tf.lite.Interpreter(model_path="./models/auto_detect_model.tflite")
        self.interpreter.allocate_tensors()  # Викликайте allocate_tensors тут

        # Отримайте деталі входу та виходу
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict_image(self, image_path):
        # Завантажте та підготуйте зображення
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Додайте вимір для пакетного розміру
        img_array = img_array.astype(np.float32) / 255.0  # Нормалізуйте пікселі

        # Встановіть вхідні дані для інтерпретатора
        self.interpreter.set_tensor(self.input_details[0]['index'], img_array)

        # Виконайте інтерпретацію
        self.interpreter.invoke()

        # Отримайте результати
        prediction = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Припустимо, що клас "1" – це "автомобіль", а клас "0" – це "не автомобіль"
        if prediction[0][0] < 0.5:  # Якщо ймовірність більше 0.5, то це автомобіль
            print("На зображенні присутній автомобіль.")
            return True
        else:
            print("На зображенні відсутній автомобіль.")
            return False


# Використання класу AutoDetector
# detector_auto = AutoDetector()
# detector_auto.predict_image("./data/photo2.jpg")

class CharacterRecognizer:
    def __init__(self, model_path="./models/plate_detect_model.tflite"):
        # Завантажте TFLite модель
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()  # Викликайте allocate_tensors тут

        # Отримайте деталі входу та виходу
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def fix_dimension(self, img):
        new_img = np.zeros((28, 28, 3))
        for i in range(3):
            new_img[:, :, i] = img
        return new_img

    def predict_image(self, img_array):
        # Переконайтеся, що зображення має правильну форму
        img_array = np.expand_dims(img_array, axis=0)  # Додайте вимір для пакетного розміру
        img_array = img_array.astype(np.float32) / 255.0  # Нормалізуйте пікселі

        # Встановіть вхідний тензор
        self.interpreter.set_tensor(self.input_details[0]['index'], img_array)

        # Виконайте передбачення
        self.interpreter.invoke()

        # Отримайте результат передбачення
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Поверніть передбачений клас
        return np.argmax(output_data, axis=1)[0]

    def segment_characters(self, chars):
        dic = {}
        characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i, c in enumerate(characters):
            dic[i] = c

        output = []
        for ch in chars:  # iterating over the characters
            img_ = cv2.resize(ch, (28, 28), interpolation=cv2.INTER_AREA)
            img = self.fix_dimension(img_)
            img = img.reshape(28, 28, 3)  # preparing image for the model

            # Виклик predict_image
            y_ = self.predict_image(img)

            character = dic[y_]  # визначаємо символ за індексом
            output.append(character)  # зберігаємо результат у список

        plate_number = ''.join(output)

        return plate_number
