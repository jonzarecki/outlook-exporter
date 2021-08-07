from typing import List, Optional

import cv2
import numpy as np
from PIL.Image import Image
from qrcode import QRCode, constants
from qrcode.util import QRData


def create_qr_image(messages: List[str]) -> Image:
    """Create QR image from a list of messages."""
    qr = QRCode(version=2, error_correction=constants.ERROR_CORRECT_L)
    for msg in messages:
        qr.add_data(QRData(msg), optimize=500)
    return qr.make_image().get_image()


_detector = None


def read_qr_from_ndarray(img: np.ndarray) -> Optional[str]:
    """Read a QR code from a numpy array image, Return None if not found/error."""
    global _detector
    if _detector is None:
        _detector = cv2.QRCodeDetector()  # initialize the cv2 QRCode detector

    # detect and decode
    data, vertices_array, _binary_qrcode = _detector.detectAndDecode(img)

    return data if vertices_array is not None else None
