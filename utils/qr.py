import qrcode
from PIL.Image import Image


def create_qr_image(msg: str) -> Image:
    """Create QR image from msg."""
    return qrcode.make(msg).get_image()
