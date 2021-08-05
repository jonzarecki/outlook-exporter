import win32com.client

from utils.google_calendar import create_gc_object, upsert_gc_event_from_outlook_entry
from utils.outlook_reader.calendar import read_calendar

if __name__ == "__main__":
    Outlook = win32com.client.Dispatch("Outlook.Application")

    # get the Namespace / Session object
    namespace = Outlook.Session  # identical to GetNameSpace("MAPI") (starting with Outlook 98)

    # get own calendar
    calendar = namespace.GetDefaultFolder(9)
    entries = read_calendar(calendar)

    # add Outlook entries to google calendar
    gc = create_gc_object()

    for outlook_entry in entries:
        print(outlook_entry)
        upsert_gc_event_from_outlook_entry(gc, outlook_entry)
