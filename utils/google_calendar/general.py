import os
from typing import Dict

from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from gcsa.google_calendar import GoogleCalendar
from google.oauth2.credentials import Credentials

from utils.config import PROJECT_ROOT

GC_SECRET_JSON_PATH = os.path.join(PROJECT_ROOT, "client_secret.apps.googleusercontent.com.json")


def create_gc_object(calendar_id: str, credentials: Credentials = None) -> GoogleCalendar:
    if credentials is not None:  # use service-account credentials (assumes $calendar_id was shared with the account)
        return GoogleCalendar(calendar=calendar_id, credentials=credentials)
    else:  # fallback to Oauth2
        return GoogleCalendar(
            calendar=calendar_id, credentials_path=GC_SECRET_JSON_PATH, authentication_flow_port=11138
        )


def get_event_possible_colors(gc: GoogleCalendar) -> Dict[str, str]:
    """Retrieves a dict of possible colors and their ids for the given calendar.

    Args:
        gc: a google calendar object

    Returns:
        Dict of color_id (can be passed to add_event()) and hex value of color (#a4bdfc)
    """
    gc_color_list = gc.list_event_colors()
    assert "1" in gc_color_list, "I assert that 1 is the default color in GC (appears in other code)"
    return {k: v["background"] for k, v in gc.list_event_colors().items()}


def _find_closest_color_id_in_gc(gc: GoogleCalendar, base_color_hex: str) -> str:
    """Returns the closest color_id to $base_color_hex from the $gc calendar."""

    def conv_to_lab(color_hex: str) -> sRGBColor:
        return convert_color(sRGBColor.new_from_rgb_hex(color_hex), LabColor)

    base_c = conv_to_lab(base_color_hex)
    return sorted(  # return closest cid
        ((cid, delta_e_cie2000(base_c, conv_to_lab(c_hex))) for cid, c_hex in get_event_possible_colors(gc).items()),
        key=lambda x: x[1],  # type: ignore
    )[0][0]
