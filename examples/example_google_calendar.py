from beautiful_date import Jan

from utils.google_calendar import create_gc_object, upsert_gc_event

if __name__ == "__main__":
    gc = create_gc_object()

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
