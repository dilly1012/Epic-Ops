from datetime import datetime

from epic_ops.jobs.coach_pay import coach_from_event_name, coach_pay_sheet
from epic_ops.jobs.fill_report import fill_report
from sample.data import SAMPLE_EVENTS, SAMPLE_REGISTRATIONS


def test_coach_from_event_name():
    assert coach_from_event_name("Clinic · L4 · Dillon") == "Dillon"
    assert coach_from_event_name("Open Play") is None


def test_flags_full_and_low_events():
    rows = {r["event_id"]: r for r in fill_report(SAMPLE_EVENTS, datetime.fromisoformat("2027-01-11T09:00:00-06:00"))}
    assert rows[1]["flag"] == "full"
    assert rows[2]["flag"] == "low"


def test_pays_per_session_not_per_player():
    lines, _ = coach_pay_sheet(SAMPLE_REGISTRATIONS)
    assert next(l for l in lines if l["coach"] == "Dillon")["sessions"] == 1
