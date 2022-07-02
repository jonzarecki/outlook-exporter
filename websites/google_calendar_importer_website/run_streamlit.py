import logging
import os
import os.path
import sys
import time
from pathlib import Path

import streamlit as st
from google.oauth2 import service_account
from stqdm import stqdm
from streamlit.report_thread import get_report_ctx

_root_path = Path(__file__).parent.parent.parent
assert _root_path.name == "outlook-exporter", "_root_path is not the actual project's root path"
sys.path.append(str(_root_path))

from utils.google_calendar.events import upsert_gc_event_from_outlook_entry  # pylint: disable=C0413
from utils.google_calendar.general import create_gc_object, GC_SECRET_JSON_PATH  # pylint: disable=C0413
from utils.streamlit_utils import streamlit_run_js  # pylint: disable=C0413
from websites.export_utils import read_exported_str_to_entry_list  # pylint: disable=C0413

logger = logging.getLogger(__name__)


def main() -> None:
    st.header("Google Calendar Importer Website")
    if not os.path.exists(GC_SECRET_JSON_PATH):
        with open(GC_SECRET_JSON_PATH, "w") as f:
            f.write(st.secrets["gc_client_secret_json"])

    ctx = get_report_ctx()
    query_str = ctx.query_string
    print("query_str\n" + query_str)
    if query_str != "":
        entry_list = read_exported_str_to_entry_list(query_str)
        st.text(str(entry_list))

        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/calendar",
            ],
        )

        gc = create_gc_object(st.secrets["gc_calendar_id"], credentials)

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
    )

    logger.setLevel(level=logging.DEBUG)  # if DEBUG else logging.INFO

    main()
