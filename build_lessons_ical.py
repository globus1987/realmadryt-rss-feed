#!/usr/bin/env python3
"""Generate an iCalendar file with the lesson plan of class 2b.

Source: printed timetable "Klasa 2b", NOWY ŚWIAT Niepubliczna Szkoła Podstawowa
w Gdańsku, ul. Nowy Świat 7a (plan generated 27.08.2026).

All events are stored as floating-with-timezone values anchored to
TZID=Europe/Warsaw, so daylight-saving transitions are handled by the calendar
application - the lessons stay at their local clock time all year.
"""

from datetime import date, datetime, timedelta

OUTPUT = "lekcje_2b.ics"

# School year covered by the plan.
FIRST_SCHOOL_DAY = date(2026, 9, 1)
LAST_SCHOOL_DAY = date(2027, 6, 25)

# Lesson number -> (start, end) as printed in the timetable header.
PERIODS = {
    0: ("07:20", "08:05"),
    1: ("08:10", "08:55"),
    2: ("09:00", "09:45"),
    3: ("09:55", "10:40"),
    4: ("10:55", "11:40"),
    5: ("11:55", "12:40"),
    6: ("12:50", "13:35"),
    7: ("13:55", "14:40"),
    8: ("15:00", "15:45"),
    9: ("15:50", "16:35"),
}

# Abbreviation used on the plan -> full subject name.
SUBJECTS = {
    "ew": "Edukacja wczesnoszkolna",
    "ang.": "Język angielski",
    "Wf": "Wychowanie fizyczne",
    "bas": "Basen",
    "muz": "Muzyka",
    "gkor": "Gimnastyka korekcyjna",
    "konw": "Konwersacje",
    "Komp": "Komputery / informatyka",
    "rel/ety": "Religia / Etyka",
}

# day name -> RRULE BYDAY, ISO weekday
DAYS = {
    "Poniedziałek": ("MO", 1),
    "Wtorek": ("TU", 2),
    "Środa": ("WE", 3),
    "Czwartek": ("TH", 4),
    "Piątek": ("FR", 5),
}

# day -> list of (period, abbreviation, teacher(s), room)
PLAN = {
    "Poniedziałek": [
        (1, "Wf", "MKR", "S gim"),
        (2, "ew", "MAB", ""),
        (3, "ew", "MAB", ""),
        (4, "ang.", "DGO", ""),
        (5, "ew", "MAB", ""),
        (6, "ew", "MAB", ""),
        (7, "ew", "MAB", ""),
    ],
    "Wtorek": [
        (2, "ew", "MAB", ""),
        (3, "ew", "MAB", ""),
        (4, "ew", "MAB", ""),
        (5, "ang.", "DGO", ""),
        (6, "bas", "BOK / KTY / MAB", ""),
        (7, "muz", "TPR", ""),
    ],
    "Środa": [
        (2, "rel/ety", "DSK / GBU", "2"),
        (3, "ang.", "DGO", ""),
        (4, "ew", "MAB", ""),
        (5, "ew", "MAB", ""),
        (6, "gkor", "MKR", "S gim"),
    ],
    "Czwartek": [
        (2, "ew", "MAB", ""),
        (3, "ew", "MAB", ""),
        (4, "konw", "CPR", ""),
        (5, "ew", "MAB", ""),
        (6, "ang.", "DGO", ""),
        (7, "Komp", "JBA", ""),
    ],
    "Piątek": [
        (2, "ew", "MAB", ""),
        (3, "ew", "MAB", ""),
        (4, "ew", "MAB", ""),
        (5, "ew", "MAB", ""),
        (6, "ew", "MAB", ""),
        (7, "ang.", "DGO", ""),
    ],
}

# Full VTIMEZONE definition so the file is self-contained for clients that do
# not carry an Olson database.
VTIMEZONE = """BEGIN:VTIMEZONE
TZID:Europe/Warsaw
X-LIC-LOCATION:Europe/Warsaw
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE"""


def first_occurrence(iso_weekday):
    """First date on/after the first school day falling on that weekday."""
    delta = (iso_weekday - FIRST_SCHOOL_DAY.isoweekday()) % 7
    return FIRST_SCHOOL_DAY + timedelta(days=delta)


def stamp(day, hhmm):
    hour, minute = hhmm.split(":")
    return "%s%sT%s%s00" % (day.strftime("%Y%m%d"), "", hour, minute)


def escape(value):
    """Escape a RFC 5545 TEXT value."""
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def fold(line):
    """RFC 5545 line folding at 75 octets."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    out, chunk = [], b""
    for char in line:
        raw = char.encode("utf-8")
        limit = 75 if not out else 74
        if len(chunk) + len(raw) > limit:
            out.append(chunk.decode("utf-8"))
            chunk = b""
        chunk += raw
    out.append(chunk.decode("utf-8"))
    return "\r\n ".join(out)


def build():
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    until = (
        datetime.combine(LAST_SCHOOL_DAY + timedelta(days=1), datetime.min.time())
        .strftime("%Y%m%dT%H%M%SZ")
    )

    caldesc = escape(
        "NOWY ŚWIAT Niepubliczna Szkoła Podstawowa w Gdańsku, "
        "ul. Nowy Świat 7a. Plan wygenerowany 27.08.2026."
    )

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//realmadryt-rss-feed//Plan lekcji 2b//PL",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Plan lekcji - Klasa 2b",
        "X-WR-TIMEZONE:Europe/Warsaw",
        "X-WR-CALDESC:%s" % caldesc,
    ]
    lines += VTIMEZONE.split("\n")

    for day, lessons in PLAN.items():
        byday, iso_weekday = DAYS[day]
        start_date = first_occurrence(iso_weekday)
        for period, abbr, teacher, room in lessons:
            begin, end = PERIODS[period]
            subject = SUBJECTS[abbr]
            uid = "2b-%s-%d-%s@realmadryt-rss-feed" % (byday.lower(), period, abbr.strip(".").lower())
            description = escape(
                "Lekcja %d (%s-%s)\nNauczyciel: %s" % (period, begin, end, teacher)
            )
            lines += [
                "BEGIN:VEVENT",
                "UID:%s" % uid,
                "DTSTAMP:%s" % now,
                "DTSTART;TZID=Europe/Warsaw:%s" % stamp(start_date, begin),
                "DTEND;TZID=Europe/Warsaw:%s" % stamp(start_date, end),
                "RRULE:FREQ=WEEKLY;BYDAY=%s;UNTIL=%s" % (byday, until),
                "SUMMARY:%s" % escape(subject),
                "DESCRIPTION:%s" % description,
                "CATEGORIES:Klasa 2b",
                "TRANSP:OPAQUE",
            ]
            if room:
                lines.append("LOCATION:%s" % escape(room))
            lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(line) for line in lines) + "\r\n"


if __name__ == "__main__":
    with open(OUTPUT, "w", encoding="utf-8", newline="") as handle:
        handle.write(build())
    print("wrote %s" % OUTPUT)
