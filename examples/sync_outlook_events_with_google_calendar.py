import win32com.client

from utils.google_calendar.events import sync_outlook_events_with_gc
from utils.google_calendar.general import create_gc_object
from utils.outlook_reader.calendar import read_local_outlook_calendar

if __name__ == "__main__":
    Outlook = win32com.client.Dispatch("Outlook.Application")

    # get the Namespace / Session object
    namespace = Outlook.Session  # identical to GetNameSpace("MAPI") (starting with Outlook 98)

    # get own calendar
    calendar = namespace.GetDefaultFolder(9)
    days_ahead = 7
    entries = read_local_outlook_calendar(calendar, days_ahead=days_ahead)
    gc = create_gc_object("primary")

    sync_outlook_events_with_gc(gc, entries)
