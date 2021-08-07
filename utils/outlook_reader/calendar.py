import datetime
from dataclasses import dataclass, field
from typing import List

import win32com.client
from pywintypes import TimeType

from utils.outlook_reader.general import (
    BUSYSTATUS_ENUM,
    OUTLOOK_COLOR_ENUM,
    generate_outlook_namespace,
)


@dataclass
class OutlookCalendarEntry:
    subject: str
    start_date: datetime.datetime
    end_date: datetime.datetime

    location: str = ""
    organizer: str = ""
    busystatus: str = ""

    attendees: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    categories_colors: List[str] = field(default_factory=list)
    conversation_id: str = ""

    def __str__(self) -> str:
        return (
            f"{self.subject}: {self.start_date}-{self.end_date} \n"
            f"{self.location}, {self.organizer}, {self.busystatus} \n"
            f"{self.attendees}\n"
            f"{list(zip(self.categories, self.categories_colors))}\n"
            f"{self.conversation_id}"
        )

    def export_as_str(self) -> str:
        params = self.__dict__.copy()
        params["start_date"] = params["start_date"].isoformat()
        params["end_date"] = params["end_date"].isoformat()

        repr_s = str([v for (k, v) in sorted(params.items(), key=lambda itm: itm[0])])
        assert OutlookCalendarEntry.import_from_char(repr_s) == self, "import and export should be equal"
        return repr_s

    @staticmethod
    def import_from_char(repr_s: str) -> "OutlookCalendarEntry":
        values = eval(repr_s)  # pylint: disable=W0123
        keys = sorted(OutlookCalendarEntry.__annotations__.keys())
        params = dict(zip(keys, values))
        assert isinstance(params, dict), "exported string should contain a string of a dict items"

        params["start_date"] = datetime.datetime.fromisoformat(params["start_date"])
        params["end_date"] = datetime.datetime.fromisoformat(params["end_date"])
        return OutlookCalendarEntry(**params)


def get_category_color(cat_name: str, namespace: win32com.client.CDispatch = None) -> str:
    """Extract the category color (in hex) for $cat_name from the current user."""
    namespace = generate_outlook_namespace() if namespace is None else namespace
    for cat in namespace.Categories:
        if cat.Name == cat_name:
            return OUTLOOK_COLOR_ENUM[cat.Color]
    else:
        raise ValueError(f"{cat_name} is not a valid outlook category name")


def get_current_user_outlook_calendar() -> win32com.client.CDispatch:
    """Get Outlook calendar for current user."""
    namespace = generate_outlook_namespace()
    return namespace.GetDefaultFolder(9)


def read_local_outlook_calendar(calendar: win32com.client.CDispatch, days_ahead: int = 7) -> List[OutlookCalendarEntry]:
    """Read local outlook calendar events during the next $days_ahead days.

    Args:
        calendar: The Calendar folder to use.
        days_ahead: The number of days ahead to read from the calendar

    Returns:
        List of CalendarEntries with read information
    """
    # Get the AppointmentItem objects
    # http://msdn.microsoft.com/en-us/library/office/aa210899(v=office.11).aspx
    items = calendar.Items

    # Restrict to items in the next $days_ahead days
    begin = datetime.date.today()
    end = begin + datetime.timedelta(days=days_ahead)
    restriction = "[Start] >= '" + begin.strftime("%d/%m/%Y") + "' AND [End] <= '" + end.strftime("%d/%m/%Y") + "'"
    restricted_items = items.Restrict(restriction)

    def format_attendees_to_list(att_list: str) -> List[str]:
        return att_list.split("; ") if att_list != "" else []  # TODO: clean attendees names

    def format_categories_to_list(cat_list: str) -> List[str]:
        return cat_list.split(", ") if cat_list != "" else []

    def convert_pywintypes_datetime_to_datetime(
        pywin_dt: TimeType, o_timezone: win32com.client.CDispatch
    ) -> datetime.datetime:
        timezone = datetime.timezone(datetime.timedelta(minutes=-(o_timezone.Bias + o_timezone.DaylightBias)))
        return datetime.datetime.fromisoformat(pywin_dt.isoformat()[:-9]).astimezone(timezone)  # remove +03:00 from iso

    # Read items - Note that Outlook might prevent access to individual
    # item attributes, such as "Organizer", while access to other attributes of
    # the same item is granted.
    calendar_entries = []
    for appointment_item in restricted_items:
        start_date = convert_pywintypes_datetime_to_datetime(appointment_item.Start, appointment_item.StartTimeZone)
        end_date = convert_pywintypes_datetime_to_datetime(appointment_item.End, appointment_item.EndTimeZone)
        subject = appointment_item.Subject
        opt_attendees = format_attendees_to_list(appointment_item.OptionalAttendees)
        required_attendees = format_attendees_to_list(appointment_item.RequiredAttendees)
        busystatus = BUSYSTATUS_ENUM[appointment_item.BusyStatus]
        location = appointment_item.Location
        organizer = appointment_item.Organizer
        categories = format_categories_to_list(appointment_item.Categories)
        conversation_id = appointment_item.ConversationID  # maybe an ID resilient to reschedules

        entry = OutlookCalendarEntry(
            subject,
            start_date,
            end_date,
            location,
            organizer,
            busystatus,
            required_attendees + opt_attendees,
            categories,
            [get_category_color(cat_name) for cat_name in categories],
            conversation_id,
        )
        calendar_entries.append(entry)

    return calendar_entries
