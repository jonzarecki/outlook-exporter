from typing import Iterable, Optional

import win32com.client


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

    Example:
        get shared calendar through folder tree
        print("Shared calendar")
        print("---------------")
        sharedCalendar = findFolder(namespace.Folders, ["Internet Calendars", "Norfeld@so.com"])
        printCalendar(sharedCalendar)
    """
    for folder in folders:
        if folder.Name == search_path[level]:
            if level < len(search_path) - 1:
                # Search sub folder
                folder = find_folder(folder.folders, search_path, level + 1)
            return folder
    return None
