import win32com.client

from utils.google_calendar.events import upsert_gc_event_from_outlook_entry
from utils.google_calendar.general import create_gc_object
from utils.outlook_reader.calendar import read_local_outlook_calendar

if __name__ == "__main__":
    Outlook = win32com.client.Dispatch("Outlook.Application")

    # get the Namespace / Session object
    namespace = Outlook.Session  # identical to GetNameSpace("MAPI") (starting with Outlook 98)

    # get own calendar
    calendar = namespace.GetDefaultFolder(9)
    entries = read_local_outlook_calendar(calendar)

    # add Outlook entries to google calendar
    gc = create_gc_object("primary")

    for outlook_entry in entries:
        print(outlook_entry)
        upsert_gc_event_from_outlook_entry(gc, outlook_entry)
