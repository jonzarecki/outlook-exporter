import pythoncom
import win32com.client


def generate_outlook_namespace() -> win32com.client.CDispatch:
    """Generate outlook session for currently logged in user."""
    pythoncom.CoInitialize()  # in-case this function runs in a new process/thread
    outlook = win32com.client.Dispatch("Outlook.Application")
    return outlook.Session  # identical to GetNameSpace("MAPI") (starting with Outlook 98)


# https://www.slipstick.com/developer/print-list-categories-colors/
RED = "#F07D88"
ORANGE = "#FF8C00"
YELLOW = "#FFF100"
GREEN = "#5FBE7D"
BLUE = "#55ABE5"
PURPLE = "#A895E2"
MAROON = "#E48BB5"
GRAY = "#ABABAB"
BLACK = "#474747"
NO_COLOR = "NO_COLOR"

OUTLOOK_COLOR_ENUM = {
    15: BLACK,
    8: BLUE,
    0: NO_COLOR,
    5: GREEN,
    13: GRAY,
    2: ORANGE,
    1: RED,
    10: MAROON,
    9: PURPLE,
}

FREE = "Free"
TENTATIVE = "Tentative"
BUSY = "Busy"
OUT_OF_OFFICE = "OutOfOffice"
ELSEWHERE = "WorkingElsewhere"

# https://docs.microsoft.com/en-us/office/vba/api/outlook.olbusystatus
BUSYSTATUS_ENUM = {
    0: FREE,
    1: TENTATIVE,
    2: BUSY,
    3: OUT_OF_OFFICE,
    4: ELSEWHERE,
}
