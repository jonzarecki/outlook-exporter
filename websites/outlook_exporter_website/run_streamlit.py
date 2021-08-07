import streamlit as st

from utils.outlook_reader.calendar import (
    get_current_user_outlook_calendar,
    read_local_outlook_calendar,
)
from utils.qr import create_qr_image
from websites.shared import export_entry_list_as_str

if __name__ == "__main__":
    st.header("Outlook Exporter")
    days_ahead = st.number_input("Enter number of days ahead to export", value=7, min_value=1, max_value=14)
    calendar = get_current_user_outlook_calendar()
    entries = read_local_outlook_calendar(calendar, days_ahead)

    exported_str = export_entry_list_as_str(entries)
    st.text(exported_str)
    st.text(str(len(exported_str)))

    st.image(
        create_qr_image(["http://172.16.0.116:8501?", exported_str]),
        caption="qr code",
    )
