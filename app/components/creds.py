import os
import time

import cv2
import numpy as np
#import pytesseract
from easyocr import Reader


class GetCreds():
    def __init__(self):
        self.reader = Reader(["en"])
        # pass

    def cleanup_text(self, text):
        #strip out non-ASCII text
        return "".join([c if ord(c) < 128 else "" for c in text]).strip()

    def clean_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, None, fx=8, fy=8,interpolation=cv2.INTER_CUBIC)
        frame = cv2.bilateralFilter(frame, 9, 75, 75)
        frame = cv2.threshold(frame, 240, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        kernel = np.ones((4, 4), np.uint8)
        frame = cv2.dilate(frame, kernel, iterations=1)
        frame = cv2.erode(frame, kernel, iterations=1)
        frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)
        #cv2.imshow("frame", frame) #SHOW frame
        #cv2.waitKey()
        return frame

    def process_frame(self, frame, side):
        all_cpoints = []
        if side == "top":
            y_start = 339
            y_end = 372
        else:
            y_start = 570
            y_end = y_start + 33
        for agent_row in range(0, 5):
            cropped_cred_image = frame[y_start:y_end, 1175:1293]
            #cv2.imshow("Image", cropped_cred_image)
            #cv2.waitKey()
            #pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
                #cpoints = pytesseract.image_to_string(cropped_cred_image, lang='ng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
            #print("points: ", points)
            cpoints = self.reader.readtext(self.clean_frame(cropped_cred_image),allowlist ='0123456789')
            cpoints = {"credits": cpoints[0][1], "confidence": cpoints[0][2]}
            #print(cpoints)
            all_cpoints.append(cpoints)
            y_start = y_start + 33
            y_end = y_start + 33
        return all_cpoints

    def get_creds(self, frame):
        all_creds = {"top": [], "bottom": []}
        all_creds["top"] = self.process_frame(frame, "top")
        all_creds["bottom"] = self.process_frame(frame,"bottom")
        return all_creds



if __name__ == "__main__":
    get_Credits = GetCreds()
    tab_images_directory = os.path.abspath(os.path.join(__file__, "../../test_images/Tab Images/"))
    for i in range(2, 10):
        start = time.time()
        image = cv2.imread('{}/{}.png'.format(tab_images_directory, i))
        print("===================Image No. {}===================".format(i))
        all_cpoints=get_Credits.get_creds(image)
        print("identified Credits", all_cpoints)
        end = time.time()
        print("Time elasped", end - start)
    #for i in range(2, 10):
        #image = cv2.imread("Tab Images/{}.png".format(i))
        #gc.get_creds(image)
        # cv2.imshow("Image",image[383:410,1239:1321])
        # cv2.waitKey()
