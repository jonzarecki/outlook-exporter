import pythoncom
import win32com.client


def generate_outlook_namespace() -> win32com.client.CDispatch:
    """Generate outlook session for currently logged in user."""
    pythoncom.CoInitialize()  # in-case this function runs in a new process/thread
    outlook = win32com.client.Dispatch("Outlook.Application")
    return outlook.Session  # identical to GetNameSpace("MAPI") (starting with Outlook 98)
