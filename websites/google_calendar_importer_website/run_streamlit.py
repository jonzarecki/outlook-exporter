import logging
import os.path

import streamlit as st

from utils.google_calendar import (
    GC_SECRET_JSON_PATH,
    create_gc_object,
    upsert_gc_event_from_outlook_entry,
)
from utils.outlook_reader.calendar import OutlookCalendarEntry

logger = logging.getLogger(__name__)

SPLIT_STR = "984651651"


def main():
    st.header("Google Calendar Importer Website")
    if not os.path.exists(GC_SECRET_JSON_PATH):
        with open(GC_SECRET_JSON_PATH, "w") as f:
            f.write(st.secrets["gc_client_secret_json"])

    query_params = st.experimental_get_query_params()

    if "qr_str" in query_params:
        exporter_str = query_params["qr_str"][0]
        assert (
            exporter_str[: len(st.secrets["unique_identifier"])] == st.secrets["unique_identifier"]
        ), "QR code was generated with this id at the beginning"

        exporter_str = exporter_str[len(st.secrets["unique_identifier"]) :]
        entry_list = [OutlookCalendarEntry.import_from_char(repr_s) for repr_s in exporter_str.split(SPLIT_STR)]
        st.text(str(entry_list))

        gc = create_gc_object(st.secrets["gc_calendar_id"])

        for outlook_entry in entry_list:
            print(outlook_entry)
            upsert_gc_event_from_outlook_entry(gc, outlook_entry)

    else:
        st.text("no qr_str")


if __name__ == "__main__":
    import os

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: " "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    main()
