import hashlib
import logging
import os
from datetime import datetime
from typing import Dict, Optional

import googleapiclient.errors
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar

from utils.config import PROJECT_ROOT
from utils.outlook_reader.calendar import OutlookCalendarEntry
from utils.outlook_reader.general import BUSY, ELSEWHERE, OUT_OF_OFFICE, TENTATIVE

GC_SECRET_JSON_PATH = os.path.join(PROJECT_ROOT, "client_secret.apps.googleusercontent.com.json")


def create_gc_object(calendar_id: str) -> GoogleCalendar:
    return GoogleCalendar(calendar=calendar_id, credentials_path=GC_SECRET_JSON_PATH)


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

    def conv_to_lab(color_hex: str):
        return convert_color(sRGBColor.new_from_rgb_hex(color_hex), LabColor)

    base_c = conv_to_lab(base_color_hex)
    return sorted(  # return closest cid
        ((cid, delta_e_cie2000(base_c, conv_to_lab(c_hex))) for cid, c_hex in get_event_possible_colors(gc).items()),
        key=lambda x: x[1],
    )[0][0]


def upsert_gc_event_from_outlook_entry(
    gc: GoogleCalendar, entry: OutlookCalendarEntry, del_if_exists: bool = True
) -> Event:
    """Upserts a event to the calendar with the specified conversation_id.

    If del_if_exists=True also keeps the old one(s)
    Args:
        gc: google calendar object
        entry: outlook calendar entry to add
        del_if_exists: Whether to delete older events created with "the same id"

    Returns:
        The created event's Event object.
    """
    return upsert_gc_event(
        gc,
        event_id=hashlib.md5(entry.conversation_id.encode()).hexdigest(),
        summary=entry.subject,
        start_date=entry.start_date,
        end_date=entry.end_date,
        color_id=_find_closest_color_id_in_gc(gc, entry.categories_colors[0])
        if len(entry.categories_colors) != 0
        else None,
        transparency="opaque" if entry.busystatus in (BUSY, OUT_OF_OFFICE, ELSEWHERE, TENTATIVE) else "transparent",
        del_if_exists=del_if_exists,
    )


def upsert_gc_event(
    gc: GoogleCalendar,
    event_id: str,
    summary: str,
    start_date: datetime,
    end_date: datetime,
    transparency: str,
    color_id: Optional[str] = None,
    del_if_exists: bool = True,
) -> Event:
    """Upserts a event to the calendar with the specified event_id.

    If del_if_exists=True also keeps the old one(s).
    Field definition are described in https://developers.google.com/calendar/api/v3/reference/events
    Args:
        gc: google calendar object
        event_id: id string (in base32hex)
        summary: summary line to the event
        start_date: event start time in datetime
        end_date: event end time in datetime
        transparency: event transparency (opaque, transparent)
        color_id: color id for the given calendar
        del_if_exists: Whether to delete older events created with "the same id"

    Returns:
        The created event's Event object.
    """
    i = 0
    while True:
        # event_id is unique even after deletion, my convention is to add a counter after the event id
        # in order to keep track of the id.
        new_event_id = event_id + str(i)
        try:
            existing_event = gc.get_event(new_event_id)
        except googleapiclient.errors.HttpError as e:
            if e.status_code == 404:  # didn't find an event with that id
                logging.info(f'Using event_id "{new_event_id}"')
                event_id = new_event_id
                break
            raise

        if del_if_exists:
            try:
                gc.delete_event(existing_event)
            except googleapiclient.errors.HttpError as e:
                if e.status_code == 410:
                    logging.info(f'The requested event "{new_event_id}" was already deleted.')
        i += 1

    event = Event(
        id=event_id,  # used to set the event id in the google calendar server
        event_id=event_id,
        summary=summary,
        start=start_date,
        end=end_date,
        color_id=color_id,
        transparency=transparency,
        minutes_before_popup_reminder=15,
    )

    event = gc.add_event(event)
    return event
