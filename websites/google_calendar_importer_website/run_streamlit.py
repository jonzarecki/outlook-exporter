import logging
import queue
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from streamlit_webrtc import ClientSettings, WebRtcMode, webrtc_streamer
from webcam import webcam

from utils.config import PROJECT_ROOT
from utils.qr import read_qr_from_ndarray

HERE = Path(__file__).parent

logger = logging.getLogger(__name__)

WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={
        "video": True,
        "audio": False,
    },
)


def main():
    st.header("WebRTC demo")

    app_sendonly_video()

    logger.debug("=== Alive threads ===")
    for thread in threading.enumerate():
        if thread.is_alive():
            logger.debug(f"  {thread.name} ({thread.ident})")


def app_sendonly_video():
    """A sample to use WebRTC in sendonly mode."""
    webrtc_ctx = webrtc_streamer(
        key="media-constraints",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=0,
        video_receiver_size=50,
        client_settings=WEBRTC_CLIENT_SETTINGS,
    )

    image_place = st.empty()
    text_place = st.empty()
    img = webcam()
    if img is None:
        st.write("Waiting for capture...")
    else:
        img_rgb = img.__array__()
        st.write("Got an image from the webcam:")
        fname = os.path.join(PROJECT_ROOT, "examples", "qr_images", "from_webcam.png")
        cv2.imwrite(fname, img_rgb)
        image_place.image(img_rgb)
        decoded_qr = read_qr_from_ndarray(img_rgb)

        text_place.text(decoded_qr if decoded_qr is not None else f"QR not found - {time.time()}")
        logger.warning(decoded_qr)

    while True:
        if webrtc_ctx.video_receiver:
            try:
                video_frame = webrtc_ctx.video_receiver.get_frame(timeout=1)
            except queue.Empty:
                logger.warning("Queue is empty. Abort.")
                break

            img_rgb: np.ndarray = video_frame.to_ndarray(format="rgb24")
            image_place.image(img_rgb)

            decoded_qr = read_qr_from_ndarray(img_rgb)
            if decoded_qr is not None:
                fname = os.path.join(PROJECT_ROOT, "examples", "qr_images", "from_webcam.png")

                cv2.imwrite(fname, img_rgb)
            text_place.text(decoded_qr if decoded_qr is not None else f"QR not found - {time.time()}")
            logger.warning(decoded_qr)

        else:
            logger.warning("AudioReceiver is not set. Abort.")
            break


if __name__ == "__main__":
    import os

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: " "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)

    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)

    main()
