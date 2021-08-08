import datetime
from dataclasses import dataclass, field
from typing import List


@dataclass
class OutlookCalendarEntry:
    subject: str
    start_date: datetime.datetime
    end_date: datetime.datetime

    location: str = ""
    organizer: str = ""
    busystatus: str = ""

    attendees: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    categories_colors: List[str] = field(default_factory=list)
    conversation_id: str = ""

    def __str__(self) -> str:
        return (
            f"{self.subject}: {self.start_date}-{self.end_date} \n"
            f"{self.location}, {self.organizer}, {self.busystatus} \n"
            f"{self.attendees}\n"
            f"{list(zip(self.categories, self.categories_colors))}\n"
            f"{self.conversation_id}"
        )

    def export_as_str(self) -> str:
        params = self.__dict__.copy()
        params["start_date"] = params["start_date"].isoformat()
        params["end_date"] = params["end_date"].isoformat()

        repr_s = str([v for (k, v) in sorted(params.items(), key=lambda itm: itm[0])])
        assert OutlookCalendarEntry.import_from_char(repr_s) == self, "import and export should be equal"
        return repr_s

    @staticmethod
    def import_from_char(repr_s: str) -> "OutlookCalendarEntry":
        values = eval(repr_s)  # pylint: disable=W0123
        keys = sorted(OutlookCalendarEntry.__annotations__.keys())
        params = dict(zip(keys, values))
        assert isinstance(params, dict), "exported string should contain a string of a dict items"

        params["start_date"] = datetime.datetime.fromisoformat(params["start_date"])
        params["end_date"] = datetime.datetime.fromisoformat(params["end_date"])
        return OutlookCalendarEntry(**params)
