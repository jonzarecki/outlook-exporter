from typing import Optional

import cv2
import numpy as np

_detector = None


def read_qr_from_ndarray(img: np.ndarray) -> Optional[str]:
    """Read a QR code from a numpy array image, Return None if not found/error."""
    global _detector
    if _detector is None:
        _detector = cv2.QRCodeDetector()  # initialize the cv2 QRCode detector

    # detect and decode
    data, vertices_array, _binary_qrcode = _detector.detectAndDecode(img)

    return data if vertices_array is not None else None
