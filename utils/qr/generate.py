from typing import List

from PIL.Image import Image
from qrcode import constants, QRCode
from qrcode.util import QRData


def create_qr_image(messages: List[str]) -> Image:
    """Create QR image from a list of messages."""
    qr = QRCode(version=2, error_correction=constants.ERROR_CORRECT_L)
    for msg in messages:
        qr.add_data(QRData(msg), optimize=500)
    return qr.make_image().get_image()
