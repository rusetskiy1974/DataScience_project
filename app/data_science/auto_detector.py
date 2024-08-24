import tensorflow as tf
import numpy as np


class AutoDetector:
    def __init__(self, model_path="app/ds_models/auto_detect_model.tflite"):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict_image(self, image_path):
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Додайте вимір для пакетного розміру
        img_array = img_array.astype(np.float32) / 255.0  # Нормалізуйте пікселі

        self.interpreter.set_tensor(self.input_details[0]['index'], img_array)
        self.interpreter.invoke()

        # Отримайте результати
        prediction = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Припустимо, що клас "0" – це "автомобіль", а клас "1" – це "не автомобіль"
        if prediction[0][0] < 0.5:  # Якщо ймовірність більше 0.5, то це автомобіль
            print("На зображенні присутній автомобіль.")
            return True
        else:
            print("На зображенні відсутній автомобіль.")
            return False

# Використання класу AutoDetector
# detector_auto = AutoDetector()
# detector_auto.predict_image("./data/photo2.jpg")
