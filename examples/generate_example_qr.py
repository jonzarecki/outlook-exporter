from utils.qr import create_qr_image

if __name__ == "__main__":
    create_qr_image(["Some data here" * 55]).show()
