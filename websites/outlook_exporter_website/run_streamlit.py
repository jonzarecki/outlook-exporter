import streamlit as st
import urllib3.request

from utils.outlook_reader.calendar import (
    get_current_user_outlook_calendar,
    read_calendar,
)
from utils.qr import create_qr_image

if __name__ == "__main__":
    st.header("Outlook Exporter")
    calendar = get_current_user_outlook_calendar()
    entries = read_calendar(calendar)
    SPLIT_STR = "984651651"

    exported_str = st.secrets["unique_identifier"] + SPLIT_STR.join([ent.export_as_str() for ent in entries])
    st.text(exported_str)

    st.image(
        create_qr_image("http://172.16.0.116:8501?" + urllib3.request.urlencode({"qr_str": exported_str})),
        caption="qr code",
    )