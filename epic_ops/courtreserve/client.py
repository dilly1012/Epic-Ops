"""Thin client for the CourtReserve Organization API.

Endpoint names come from a public copy of the spec. Confirm them against
https://api.courtreserve.com/apihelp/index once Epic has a key.
Responses are CourtReserve's own JSON (PascalCase keys), returned as dicts.
"""

import os
import time
from typing import Any

import requests


class WriteRefused(RuntimeError):
    pass


class CourtReserve:
    def __init__(self, username: str, password: str, base_url: str = "https://api.courtreserve.com",
                 write_enabled: bool = False, max_calls_per_minute: int = 50):
        self.session = requests.Session()
        self.session.auth = (username, password)  # HTTP Basic
        self.session.headers["Accept"] = "application/json"
        self.base_url = base_url.rstrip("/")
        self.write_enabled = write_enabled  # writes are refused unless this is True
        self._gap = 60 / max_calls_per_minute  # CourtReserve allows 60 calls/min per key
        self._next = 0.0

    @classmethod
    def from_env(cls, env=os.environ) -> "CourtReserve":
        user, pw = env.get("COURTRESERVE_USERNAME"), env.get("COURTRESERVE_PASSWORD")
        if not user or not pw:
            raise RuntimeError("Set COURTRESERVE_USERNAME and COURTRESERVE_PASSWORD")
        return cls(user, pw, env.get("COURTRESERVE_BASE_URL") or "https://api.courtreserve.com",
                   write_enabled=env.get("CR_WRITE_ENABLED") == "true")

    def _throttle(self) -> None:
        now = time.monotonic()
        if self._next > now:
            time.sleep(self._next - now)
        self._next = max(now, self._next) + self._gap

    def _call(self, method: str, path: str, params: dict | None = None, body: Any = None) -> Any:
        if method != "GET" and not self.write_enabled:
            raise WriteRefused(f"{method} {path}: set CR_WRITE_ENABLED=true once the key has write access")
        self._throttle()
        params = {k: (str(v).lower() if isinstance(v, bool) else v) for k, v in (params or {}).items() if v is not None}
        res = self.session.request(method, self.base_url + path, params=params, json=body, timeout=30)
        res.raise_for_status()
        data = res.json()
        if not data.get("IsSuccessStatusCode", False):
            raise RuntimeError(f"CourtReserve {method} {path}: {data.get('ErrorMessage')}")
        return data["Data"]

    def members(self, changed_since: str | None = None) -> list[dict]:
        """All members, with custom fields and ratings (including the synced DUPR)."""
        out, page = [], 1
        while True:
            data = self._call("GET", "/api/v1/member/get", {
                "pageSize": 100, "pageNumber": page, "includeUserDefinedFields": True,
                "includeRatings": True, "createdOrUpdatedFrom": changed_since,
            })
            out += data["Members"]
            if page >= data["TotalPages"]:
                return out
            page += 1

    def events(self, start_date: str, end_date: str) -> list[dict]:
        return self._call("GET", "/api/v1/eventcalendar/eventlist", {
            "startDate": start_date, "endDate": end_date,
            "includeRegisteredPlayersCount": True, "includeRatingRestrictions": True,
        })

    def registrations(self, event_date_from: str, event_date_to: str) -> list[dict]:
        return self._call("GET", "/api/v1/eventregistrationreport/listactive",
                          {"eventDateFrom": event_date_from, "eventDateTo": event_date_to})

    def set_rating_fields(self, member: dict, rating_field_id: int, rating: str,
                          reliability_field_id: int, reliability: str) -> Any:
        """Write the exact rating ("3.62") and reliability ("85%") to their two custom fields.

        The API can't set the rating category itself; staff do that from the Monday list.
        Check whether member/update needs the full profile; if so, send all fields from members().
        """
        return self._call("PUT", "/api/v1/member/update", body={
            "OrganizationMemberId": member["OrganizationMemberId"],
            "FirstName": member["FirstName"], "LastName": member["LastName"], "Email": member["Email"],
            "CustomFields": [
                {"UserDefinedFieldId": rating_field_id, "Value": rating},
                {"UserDefinedFieldId": reliability_field_id, "Value": reliability},
            ],
        })

    def create_court_block(self, reservation_type_id: int, start: str, end: str, court_ids: list[int],
                           notes: str = "") -> Any:
        """Block courts, e.g. courts 1-6 for a Rating Night wave."""
        return self._call("POST", "/api/v1/reservation/createcourtblock", body={
            "ReservationTypeId": reservation_type_id, "Start": start, "End": end,
            "CourtIds": court_ids, "Notes": notes, "IsPrivate": False,
        })


def cr_level(member: dict, category: str) -> str | None:
    """The member's current band on the CourtReserve "Epic Rating" category, if set."""
    return next((r["ValueRatingName"] for r in member.get("Ratings") or [] if r["CategoryName"] == category), None)
