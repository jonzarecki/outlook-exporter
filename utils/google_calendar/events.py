import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional

import googleapiclient.errors
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar

from utils.google_calendar.general import _find_closest_color_id_in_gc
from utils.outlook_reader.calendar import OutlookCalendarEntry
from utils.outlook_reader.general import BUSY, ELSEWHERE, OUT_OF_OFFICE, TENTATIVE


def sync_outlook_events_with_gc(gc: GoogleCalendar, outlook_events: List[OutlookCalendarEntry]):
    """Sync outlook events taken from a given range with google calendar.

    If an event which is present in the gc in this range but not in the outlook events IS WAS DELETED.
    Delete if from gc.

    Args:
        gc: google calendar object
        outlook_events: list of outlook events
    """
    timeframe_min = min(ent.start_date for ent in outlook_events).astimezone(timezone.utc)
    timeframe_max = max(ent.end_date for ent in outlook_events).astimezone(timezone.utc)

    outlook_ids_to_sync = [hash_event_id_for_gc(ent) for ent in outlook_events]
    assert len(outlook_ids_to_sync) == len(set(outlook_ids_to_sync)), "ids should be unique"

    events_already_in_gc = list(gc.get_events(timeframe_min, timeframe_max, timezone="UTC"))
    ids_already_in_gc = [gc_e.event_id for gc_e in events_already_in_gc]
    assert len(ids_already_in_gc) == len(set(ids_already_in_gc)), "ids should be unique"

    # We assume the calendar in the same timeframe is EXACTLY the same ($outlook_id == $gc_id\d+)
    # meaning if an event in gc exists without a matching outlook event it should be DELETED
    gc_events_deleted_in_outlook = [
        gc_e for gc_e in events_already_in_gc if not any((o_id in gc_e.event_id) for o_id in outlook_ids_to_sync)
    ]

    for gc_e_to_delete in gc_events_deleted_in_outlook:
        gc.delete_event(gc_e_to_delete)

    # add Outlook entries to google calendar
    for outlook_entry in outlook_events:
        print(outlook_entry)
        upsert_gc_event_from_outlook_entry(gc, outlook_entry)


def hash_event_id_for_gc(entry: OutlookCalendarEntry) -> str:
    return hashlib.md5(entry.conversation_id.encode()).hexdigest()


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
        event_id=hash_event_id_for_gc(entry),
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
