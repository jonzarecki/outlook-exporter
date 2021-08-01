import win32com.client

from outlook_reader.calendar import print_calendar
from outlook_reader.folder import show_folder_tree

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
