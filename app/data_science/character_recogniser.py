import cv2
import numpy as np
import tensorflow as tf


class CharacterRecognizer:
    def __init__(self, model_path="app/ds_models/plate_detect_model_best.tflite"):
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


character_recognizer = CharacterRecognizer()
