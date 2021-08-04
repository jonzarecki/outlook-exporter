from beautiful_date import Jan
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar

from utils.config import PROJECT_ROOT


def create_process():
    return GoogleCalendar(
        credentials_path=fr"{PROJECT_ROOT}\examples\client_secret_119838334189-dlje9qj80mvkn0ipggkrjv05lklf2uk9.\
                            apps.googleusercontent.com.json"
    )


if __name__ == "__main__":
    gc = create_process()

    event = Event(
        id="kmruhlmcc2tvnln9gofius8jqooo1",
        event_id="kmruhlmcc2tvnln9gofius8jqooo1",
        summary="Breakfast",
        start=(1 / Jan / 2019)[13:00],
        minutes_before_email_reminder=50,
    )

    event = gc.add_event(event)

    for event in gc:
        print(event)
