import streamlit as st

from utils.outlook_reader.calendar import get_current_user_outlook_calendar, read_local_outlook_calendar
from utils.qr.generate import create_qr_image
from websites.export_storage import get_export_name, upsert_export_name
from websites.export_utils import export_entry_list_as_str

if __name__ == "__main__":
    st.header("Outlook Exporter")
    days_ahead = st.number_input("Enter number of days ahead to export", value=4, min_value=1, max_value=30)
    calendar = get_current_user_outlook_calendar()
    entries = read_local_outlook_calendar(calendar, days_ahead)

    saved_inputs = []
    for ent in entries:
        col1, col2 = st.beta_columns(2)

        col1.markdown(
            f"<h2 style='text-align: center; vertical-align: middle'>{ent.subject}</h2>", unsafe_allow_html=True
        )

        saved_val = get_export_name(conversation_id=ent.conversation_id)  # is "" if not saved
        entered_export_name = col2.text_input(
            key=f"export_name_{ent.conversation_id}", label="enter_export_name", value=saved_val
        )
        saved_inputs.append((ent.conversation_id, saved_val, entered_export_name))

    exported_str = export_entry_list_as_str(entries)
    st.text(exported_str)
    st.text(str(len(exported_str)))

    if st.button("Save export names"):
        for (conversation_id, saved_val, entered_export_name) in saved_inputs:
            if entered_export_name != saved_val:
                upsert_export_name(conversation_id, entered_export_name)
                print(f"saved new value for {entered_export_name}")

    st.image(
        create_qr_image(
            [
                "https://share.streamlit.io/jonzarecki/outlook-exporter/websites/"
                "google_calendar_importer_website/run_streamlit.py?",
                exported_str,
            ]
        ),
    )
