"""Made-up sample data for trying Epic Ops without a CourtReserve key."""

from epic_ops.models import Game

SAMPLE_PLAYERS = [  # (id, name, rating, level, rated games)
    (101, "Sample Player A", 3.48, "L3", 14),
    (102, "Sample Player B", 3.47, "L3", 22),
    (103, "Sample Player C", 3.12, "L3", 9),
    (104, "Sample Player D", 3.05, "L3", 30),
    (105, "Sample Player E", 3.52, "L4", 18),
    (106, "Sample Player F", 3.51, "L4", 12),
    (107, "Sample Player G", 3.76, "L4", 25),
    (108, "Sample Player H", 3.81, "L4", 16),
]

# One Rating Night (2nd Sunday), wave 1 on courts 1-2.
SAMPLE_GAMES = [
    Game("g1", "2027-01-10T17:15:00-06:00", "rating_night", [101, 102], [105, 106], 11, 8),
    Game("g2", "2027-01-10T17:35:00-06:00", "rating_night", [101, 103], [102, 104], 11, 6),
    Game("g3", "2027-01-10T17:55:00-06:00", "rating_night", [105, 106], [107, 108], 4, 11),
    Game("g4", "2027-01-10T18:15:00-06:00", "rating_night", [101, 107], [106, 108], 11, 9),
]


def _event(eid, name, cat, start, end, cap, reg):
    return {"EventId": eid, "EventName": name, "EventCategoryId": 0, "EventCategoryName": cat,
            "StartDateTime": start, "EndDateTime": end, "MaxRegistrants": cap, "RegisteredCount": reg}


SAMPLE_EVENTS = [
    _event(1, "Clinic · L4 · Dillon", "Clinic", "2027-01-12T16:30:00-06:00", "2027-01-12T17:30:00-06:00", 8, 8),
    _event(2, "Women's Clinic · L2 · Coach C", "Women's", "2027-01-13T11:00:00-06:00", "2027-01-13T12:00:00-06:00", 8, 3),
    _event(3, "Bootcamp · L3 · Ben", "Bootcamp", "2027-01-12T18:00:00-06:00", "2027-01-12T19:30:00-06:00", 8, 6),
    _event(4, "Clinic · L5 · Emma", "Clinic", "2027-01-11T20:00:00-06:00", "2027-01-11T21:00:00-06:00", 8, 7),
]


def _reg(event_date_id, e, member_id):
    return {"EventId": e["EventId"], "EventName": e["EventName"], "EventCategoryName": e["EventCategoryName"],
            "EventDateId": event_date_id, "StartTime": e["StartDateTime"], "EndTime": e["EndDateTime"],
            "OrganizationMemberId": member_id, "PriceToPay": 15, "PaidAmount": 15, "CancelledOnUtc": None}


SAMPLE_REGISTRATIONS = [
    _reg(11, SAMPLE_EVENTS[0], 105), _reg(11, SAMPLE_EVENTS[0], 106),
    _reg(21, SAMPLE_EVENTS[1], 103),
    _reg(31, SAMPLE_EVENTS[2], 101), _reg(31, SAMPLE_EVENTS[2], 104),
    _reg(41, SAMPLE_EVENTS[3], 108),
]
