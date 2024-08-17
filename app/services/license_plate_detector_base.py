import cv2
import numpy as np
import matplotlib.pyplot as plt


class LicensePlateDetector:
    def __init__(self, cascade_path="./models/indian_license_plate.xml"):
        self.plate_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_plate(self, img, text=""):
        plate_img = img.copy()
        roi = img.copy()
        plate_rect = self.plate_cascade.detectMultiScale(
            plate_img, scaleFactor=1.2, minNeighbors=7
        )
        plate = None
        for x, y, w, h in plate_rect:
            plate = roi[y : y + h, x : x + w, :]
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
        return plate_img, plate

    def display(self, img_, title=""):
        if img_ is None:
            print("Error: Could not load image. Please verify the path.")
            return

        img = cv2.cvtColor(img_, cv2.COLOR_BGR2RGB)
        ax = plt.subplot(111)
        ax.imshow(img)
        plt.axis("off")
        plt.title(title)
        plt.show()

    def find_contours(self, dimensions, img):
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
                char = img[intY : intY + intHeight, intX : intX + intWidth]
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


# Приклад використання:
# detector = LicensePlateDetector()
# plate_img, plate = detector.load_and_detect("path_to_image.jpg", "Sample Plate")
