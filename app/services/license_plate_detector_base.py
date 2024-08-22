import cv2
from abc import ABC
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from fastapi import HTTPException


class LicensePlateDetector:
    def __init__(self, cascade_path="app/ds_models/indian_license_plate.xml"):
        self.plate_cascade = cv2.CascadeClassifier(cascade_path)

    # def detect_plate(self, img, text=""):
    #     img = self.resize_image(img)
    #     plate_img = img.copy()
    #     roi = img.copy()
    #     # all_plates = []
    #
    #     # for scale in np.arange(1.05, 1.35, 0.05):
    #     plate_rects = self.plate_cascade.detectMultiScale(
    #         plate_img, scaleFactor=1.05, minNeighbors=8
    #     )
    #     width_max = 0  # використовується для сортування за шириною
    #     plate_max = None
    #     x_max = 0
    #     y_max = 0
    #     for x, y, w, h in plate_rects:
    #         # коєфіцієнти збільшення розміру
    #         a, b = (int(0.1 * h), int(0.1 * w))
    #         aa, bb = (int(0.1 * h), int(0.1 * w))
    #         if h > 75:  # пропускає розбиття за шириною високоякісного зображення
    #             b = 0
    #             bb = 0
    #
    #         plate = roi[y + a: y + h - aa, x + b: x + w - bb, :]
    #
    #         if width_max < w:
    #             plate_max = plate
    #             width_max = w
    #             x_max = x
    #             y_max = y
    #
    #         cv2.rectangle(plate_img, (x + 2, y), (x + w - 3, y + h - 5), (51, 224, 172), 3)
    #
    #     if text != '':
    #         h = plate_max.shape[0]
    #         plate_img = cv2.putText(plate_img, text, (x_max, y_max - h // 3),
    #                                 cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.5, (51, 224, 172), 2, cv2.LINE_AA)
    #
    #     return plate_img, plate_max

    def detect_plate(self,img, text=''):
        img = self.resize_image(img)
        plate_img = img.copy()
        roi = img.copy()
        plate_rect = self.plate_cascade.detectMultiScale(plate_img, scaleFactor=1.2, minNeighbors=7)

        best_plate = None
        max_width = 0
        min_ratio = 2.0  # Мінімальне допустиме співвідношення ширини до висоти
        max_ratio = 8.0  # Максимальне допустиме співвідношення ширини до висоти

        for (x, y, w, h) in plate_rect:
            ratio = w / h

            # Вибираємо найширший прямокутник у межах допустимого співвідношення сторін
            if min_ratio <= ratio <= max_ratio and w > max_width:
                max_width = w
                best_plate = (x, y, w, h)

            cv2.rectangle(plate_img, (x + 2, y), (x + w - 3, y + h - 5), (51, 181, 155), 3)

        if best_plate:
            x, y, w, h = best_plate

            # Розширюємо прямокутник
            expansion_factor = 0.1  # Збільшуємо ширину на 10%
            new_w = int(w * (1 + expansion_factor))
            new_x = max(0, x - (new_w - w) // 2)

            # Переконуємося, що розширений прямокутник не виходить за межі зображення
            new_x = min(new_x, img.shape[1] - new_w)

            plate = roi[y:y + h, new_x:new_x + new_w, :]

            if text != '':
                plate_img = cv2.putText(plate_img, text, (new_x - new_w // 2, y - h // 2),
                                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (51, 181, 155), 1, cv2.LINE_AA)

            # Малюємо розширений прямокутник
            cv2.rectangle(plate_img, (new_x + 2, y), (new_x + new_w - 3, y + h - 5), (0, 255, 0), 3)
        else:
            plate = None

        return plate_img, plate

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
    def resize_image(img, target_height=640):
        ratio = target_height / float(img.shape[0])
        target_width = int(img.shape[1] * ratio)
        resized = cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_AREA)
        return resized

    @staticmethod
    def find_contours(dimensions, img):
        cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        lower_width, upper_width, lower_height, upper_height = dimensions
        cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

        x_cntr_list = []
        img_res = []
        for cntr in cntrs:
            intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)
            if lower_width < intWidth < upper_width and upper_height > intHeight > lower_height:
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

        dimensions = [LP_WIDTH / 8, LP_WIDTH / 2, LP_HEIGHT / 10, 2 * LP_HEIGHT / 3]
        char_list = self.find_contours(dimensions, img_dilate)
        return char_list

    def load_and_detect(self, img, text=""):
        # img = cv2.imread(image_path)
        if img is None:
            return HTTPException(status_code=400, detail="Could not load image. Please verify the path.")
        plate_img, plate = self.detect_plate(img, text)
        chars_list = detector.segment_characters(plate)
        plate_text = recognizer.segment_characters(chars_list)
        self.display(plate_img, "Detected Plate")
        return {"result": plate_text}


class CharacterRecognizer:
    def __init__(self, model_path="app/ds_models/plate_detect_model_new.tflite"):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    @staticmethod
    def fix_dimension(img):
        new_img = np.zeros((28, 28, 1))
        for i in range(1):
            new_img[:, :, i] = img
        return new_img

    def predict_image(self, img_array):
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array.astype(np.float32) / 255.0
        self.interpreter.set_tensor(self.input_details[0]['index'], img_array)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

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
            img = img.reshape(28, 28, 1)

            y_ = self.predict_image(img)

            character = dic[y_]  # визначаємо символ за індексом
            output.append(character)  # зберігаємо результат у список

        plate_number = ''.join(output)

        return plate_number


recognizer = CharacterRecognizer()

detector = LicensePlateDetector()


class AutoDetector:
    def __init__(self, model_path="./models/plate_detect_model_new.tflite"):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict_image(self, image_path):
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
