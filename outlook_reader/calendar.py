import datetime
from typing import List

import win32com.client


def print_calendar(folder: win32com.client.CDispatch):
    """Prints calendar events during the next 30 days.

    Args:
        folder: The Calendar folder to use.
    """
    # Get the AppointmentItem objects
    # http://msdn.microsoft.com/en-us/library/office/aa210899(v=office.11).aspx
    items = folder.Items

    # Restrict to items in the next 30 days
    begin = datetime.date.today()
    end = begin + datetime.timedelta(days=30)
    restriction = "[Start] >= '" + begin.strftime("%m/%d/%Y") + "' AND [End] <= '" + end.strftime("%m/%d/%Y") + "'"
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

    # Print items - Note that Outlook might prevent access to individual
    # item attributes, such as "Organizer", while access to other attributes of
    # the same item is granted.
    for appointment_item in restricted_items:
        start_date = appointment_item.Start
        end_date = appointment_item.End
        subject = appointment_item.Subject
        opt_attendees = format_attendees_to_list(appointment_item.OptionalAttendees)
        required_attendees = format_attendees_to_list(appointment_item.RequiredAttendees)
        busystatus = busystatus_enum[appointment_item.BusyStatus]
        location = appointment_item.Location
        organizer = appointment_item.Organizer
        categories = format_categories_to_list(appointment_item.Categories)
        conversation_id = appointment_item.ConversationID  # maybe an ID resilient to reschedules
        print(
            f"{subject}: {start_date}-{end_date} \n"
            f"{location}, {organizer}, {busystatus} \n"
            f"{required_attendees + opt_attendees} \n"
            f"{categories}\n"
            f"{conversation_id}"
        )
