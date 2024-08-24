import cv2
import numpy as np


class LicensePlateDetector:
    def __init__(self, cascade_path="app/ds_models/indian_license_plate.xml"):
        self.plate_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_plate(self, img):
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
            expansion_factor = 0.5  # Збільшуємо ширину на 50%
            new_w = int(w * (1 + expansion_factor))
            new_x = max(0, x - (new_w - w) // 2)

            # Переконуємося, що розширений прямокутник не виходить за межі зображення
            new_x = min(new_x, img.shape[1] - new_w)

            plate = roi[y:y + h, new_x:new_x + new_w, :]

        else:
            plate = None

        return plate

    @staticmethod
    def find_contours(dimensions, img):

        i_width_threshold = 6
        # Знайдіть всі контури на зображенні
        cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        lower_width = dimensions[0]
        upper_width = dimensions[1]
        lower_height = dimensions[2]
        upper_height = dimensions[3]

        cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:16]

        # бінарне зображення номерного знака на вхід: щоб перетворити img.shape(h,w) на img.shape(h,w,3)
        ii = np.dstack([img] * 3)

        x_cntr_list = []
        target_contours = []
        img_res = []
        for cntr in cntrs:
            # виявлення контуру на бінарному зображенні і повернення координат прямокутника, який його оточує
            intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

            # перевірка розмірів контуру для фільтрації символів за розміром контуру
            if upper_width > intWidth >= i_width_threshold and lower_height < intHeight < upper_height:
                x_cntr_list.append(intX)
                char_copy = np.zeros((44, 24))

                char = img[intY:intY + intHeight, intX:intX + intWidth]

                if lower_width > intWidth >= i_width_threshold:
                    i_char = cv2.resize(char, (intWidth, 42), interpolation=cv2.INTER_LINEAR_EXACT)

                    char = np.full((42, 22), 255, dtype=np.uint8)
                    begin = int((22 - intWidth) / 2)  # center alignment
                    char[:, begin:begin + intWidth] = i_char[:, :]
                else:
                    char = cv2.resize(char, (22, 42), interpolation=cv2.INTER_LINEAR_EXACT)

                cv2.rectangle(ii, (intX, intY), (intWidth + intX, intY + intHeight), (50, 21, 200), 2)
                # plt.imshow(ii, cmap='gray')

                char = cv2.subtract(255, char)

                # Resize the image to 24x44 with black border
                char_copy[1:43, 1:23] = char
                char_copy[0:1, :] = 0
                char_copy[:, 0:1] = 0
                char_copy[43:44, :] = 0
                char_copy[:, 23:24] = 0

                img_res.append(char_copy)  # List that stores the character's binary image (unsorted)
                if len(img_res) >= 10:
                    break

        indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
        img_res_copy = []
        for idx in indices:
            img_res_copy.append(img_res[idx])  # stores character images according to their index
        img_res = np.array(img_res_copy)

        return img_res

    def segment_characters(self, image):

        # Preprocess cropped license plate image
        img_lp = cv2.resize(image, (333, 65))
        img_gray_lp = cv2.cvtColor(img_lp, cv2.COLOR_BGR2GRAY)
        _, img_binary_lp = cv2.threshold(img_gray_lp, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_binary_lp = cv2.erode(img_binary_lp, (3, 3))
        img_binary_lp = cv2.dilate(img_binary_lp, (3, 3))

        LP_WIDTH = img_binary_lp.shape[0]
        LP_HEIGHT = img_binary_lp.shape[1]

        # Make borders white
        img_binary_lp[0:3, :] = 255
        img_binary_lp[:, 0:3] = 255
        img_binary_lp[72:75, :] = 255
        img_binary_lp[:, 330:333] = 255

        # Estimations of character contours sizes of cropped license plates
        dimensions = [LP_WIDTH / 6,
                      LP_WIDTH / 1,
                      LP_HEIGHT / 10,
                      2 * LP_HEIGHT / 3]
        # plt.imshow(img_binary_lp, cmap='gray')
        # plt.show()
        cv2.imwrite('contour.jpg', img_binary_lp)

        # Get contours within cropped license plate
        char_list = self.find_contours(dimensions, img_binary_lp)

        return char_list


plate_detector = LicensePlateDetector()
