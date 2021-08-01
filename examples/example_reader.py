import datetime
from typing import Iterable, List, Optional

import win32com.client

# based on https://github.com/afester/StackOverflow/blob/master/Python/Win32Com/COMsample.py


def show_folder_tree(folders: Iterable[win32com.client.CDispatch], indent: int = 0):  # noqa
    """Displays all available folders in a tree structure.

    Args:
        folders: The current Folders iterator
        indent: The current indent level
    """
    prefix = " " * (indent * 2)
    i = 0
    for folder in folders:
        print(f"{prefix}{i}. {folder.Name} ({folder.DefaultItemType})")
        show_folder_tree(folder.Folders, indent + 1)
        i = i + 1


def find_folder(
    folders: Iterable[win32com.client.CDispatch], search_path: str, level: int = 0
) -> Optional[win32com.client.CDispatch]:
    """Find a folder by following a given  folder path.

    Args:
        folders: The Folders iterator
        search_path: The search path - a string array with the folder names
        level: The current search level

    Returns:
        Folder if found, else None
    """
    for folder in folders:
        if folder.Name == search_path[level]:
            if level < len(search_path) - 1:
                # Search sub folder
                folder = find_folder(folder.folders, search_path, level + 1)
            return folder
    return None


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


if __name__ == "__main__":
    # get Outlook application object
    Outlook = win32com.client.Dispatch("Outlook.Application")
    print(f"Outlook version: {Outlook.Version}")
    print(f"Default profile name: {Outlook.DefaultProfileName}")

    # get the Namespace / Session object
    namespace = Outlook.Session  # identical to GetNameSpace("MAPI") (starting with Outlook 98)
    print(f"Current profile name: {namespace.CurrentProfileName}")

    ##### Show tree of all available folders
    print("\nFolders")
    print("-------")
    show_folder_tree(namespace.Folders)

    ##### get own calendar and print all entries in the next 30 days
    print("\nMy calendar")
    print("---------------")
    calendar = namespace.GetDefaultFolder(9)
    print_calendar(calendar)
