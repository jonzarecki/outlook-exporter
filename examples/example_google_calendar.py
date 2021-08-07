from beautiful_date import Jan

from utils.google_calendar.events import upsert_gc_event
from utils.google_calendar.general import create_gc_object

if __name__ == "__main__":
    gc = create_gc_object("primary")

    event = upsert_gc_event(
        gc,
        event_id="kmruhlmcc2tvnln9gofius8jqooo1",
        summary="Breakfast",
        start_date=(1 / Jan / 2019)[13:00],
        end_date=(1 / Jan / 2019)[14:00],
        transparency="opaque",
    )
    for event in gc:
        print(event)
