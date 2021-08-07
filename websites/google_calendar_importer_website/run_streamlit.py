import logging
import os
import os.path
import time

import streamlit as st
from stqdm import stqdm
from streamlit.report_thread import get_report_ctx

from utils.google_calendar.events import upsert_gc_event_from_outlook_entry
from utils.google_calendar.general import GC_SECRET_JSON_PATH, create_gc_object
from utils.streamlit_utils import streamlit_run_js
from websites.export_utils import read_exported_str_to_entry_list

logger = logging.getLogger(__name__)


def main():
    st.header("Google Calendar Importer Website")
    if not os.path.exists(GC_SECRET_JSON_PATH):
        with open(GC_SECRET_JSON_PATH, "w") as f:
            f.write(st.secrets["gc_client_secret_json"])

    ctx = get_report_ctx()
    query_str = ctx.query_string
    if query_str != "":
        entry_list = read_exported_str_to_entry_list(query_str)
        st.text(str(entry_list))

        gc = create_gc_object(st.secrets["gc_calendar_id"])

        for outlook_entry in stqdm(entry_list):
            print(outlook_entry)
            upsert_gc_event_from_outlook_entry(gc, outlook_entry)
        st.balloons()
        st.success("DONE!")
        time.sleep(2)
        streamlit_run_js("window.close();")

    else:
        st.error("URL was not sent correctly")


if __name__ == "__main__":
    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: " "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    main()
