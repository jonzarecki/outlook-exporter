import os

import cv2

from utils.qr import read_qr_from_ndarray


def read_qr_code(fname: str):
    # read the QRCODE image
    image = cv2.imread(fname)
    data = read_qr_from_ndarray(image)

    if data is not None:
        print("QRCode data:")
        print(data)
    else:
        print("There was some error")


read_qr_code(os.path.join("qr_images", "qr_code.png"))
read_qr_code(os.path.join("qr_images", "qr_code_diff_position.png"))
# "multi_diff_r.png" - works with multi, "curved.png" - doesn't work with curved
