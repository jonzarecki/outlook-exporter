import datetime
from dataclasses import dataclass
from typing import List

import win32com.client

from utils.outlook_reader.general import generate_outlook_namespace


@dataclass
class CalendarEntry:
    subject: str
    start_date: str
    end_date: str

    location: str
    organizer: str
    busystatus: str

    attendees: List[str]
    categories: List[str]
    conversation_id: str

    def __str__(self) -> str:
        return (
            f"{self.subject}: {self.start_date}-{self.end_date} \n"
            f"{self.location}, {self.organizer}, {self.busystatus} \n"
            f"{self.attendees}\n"
            f"{self.categories}\n"
            f"{self.conversation_id}"
        )

    def export_as_str(self) -> str:
        repr_s = str([v for (k, v) in sorted(self.__dict__.items(), key=lambda itm: itm[0])])
        assert CalendarEntry.import_from_char(repr_s) == self, "import and export should be equal"
        return repr_s

    @staticmethod
    def import_from_char(repr_s: str) -> "CalendarEntry":
        values = eval(repr_s)  # pylint: disable=W0123
        keys = sorted(CalendarEntry.__annotations__.keys())
        params = dict(zip(keys, values))
        assert isinstance(params, dict), "exported string should contain a string of a dict items"
        return CalendarEntry(**params)


def get_current_user_outlook_calendar() -> win32com.client.CDispatch:
    """Get Outlook calendar folders for current user."""
    namespace = generate_outlook_namespace()
    return namespace.GetDefaultFolder(9)


def print_calendar(calendar: win32com.client.CDispatch):
    """Print calendar events during the next 30 days.

    Args:
        calendar: The Calendar folder to use.
    """
    for entry in read_calendar(calendar):
        print(entry)


def read_calendar(calendar: win32com.client.CDispatch) -> List[CalendarEntry]:
    """Read calendar events during the next 30 days.

    Args:
        calendar: The Calendar folder to use.

    Returns:
        List of CalendarEntries with read information
    """
    # Get the AppointmentItem objects
    # http://msdn.microsoft.com/en-us/library/office/aa210899(v=office.11).aspx
    items = calendar.Items

    # Restrict to items in the next 30 days
    begin = datetime.date.today()
    end = begin + datetime.timedelta(days=30)
    restriction = "[Start] >= '" + begin.strftime("%d/%m/%Y") + "' AND [End] <= '" + end.strftime("%d/%m/%Y") + "'"
    restricted_items = items.Restrict(restriction)

    # https://docs.microsoft.com/en-us/office/vba/api/outlook.olbusystatus
    busystatus_enum = {
        0: "Free",
        1: "Tentative",
        2: "Busy",
        3: "OutOfOffice",
        4: "WorkingElsewhere",
    }

    def format_attendees_to_list(att_list: str) -> List[str]:
        return att_list.split("; ") if att_list != "" else []  # TODO: clean attendees names

    def format_categories_to_list(cat_list: str) -> List[str]:
        return cat_list.split(".") if cat_list != "" else []  # TODO: clean attendees names

    # Read items - Note that Outlook might prevent access to individual
    # item attributes, such as "Organizer", while access to other attributes of
    # the same item is granted.
    calendar_entries = []

    for appointment_item in restricted_items:
        start_date = appointment_item.Start.isoformat()
        end_date = appointment_item.End.isoformat()
        subject = appointment_item.Subject
        opt_attendees = format_attendees_to_list(appointment_item.OptionalAttendees)
        required_attendees = format_attendees_to_list(appointment_item.RequiredAttendees)
        busystatus = busystatus_enum[appointment_item.BusyStatus]
        location = appointment_item.Location
        organizer = appointment_item.Organizer
        categories = format_categories_to_list(appointment_item.Categories)
        conversation_id = appointment_item.ConversationID  # maybe an ID resilient to reschedules

        entry = CalendarEntry(
            subject,
            start_date,
            end_date,
            location,
            organizer,
            busystatus,
            required_attendees + opt_attendees,
            categories,
            conversation_id,
        )
        calendar_entries.append(entry)

    return calendar_entries
