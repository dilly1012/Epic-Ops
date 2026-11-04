"""Runs the whole Epic Ops loop on sample data: Rating Night -> ratings -> Monday list -> reports."""

from datetime import datetime

from epic_ops.jobs.coach_pay import coach_pay_sheet
from epic_ops.jobs.fill_report import fill_by_category, fill_report
from epic_ops.jobs.monday_list import format_monday_list, monday_level_list
from epic_ops.models import Player
from epic_ops.rating.elo import apply_game, fmt
from epic_ops.rating.levels import ranked_tiers
from epic_ops.rating.reliability import reliability, reliability_label
from sample.data import SAMPLE_EVENTS, SAMPLE_GAMES, SAMPLE_PLAYERS, SAMPLE_REGISTRATIONS


def main() -> None:
    players = {pid: Player(pid, name, rating, level, games, last_rated_game_at="2026-12-27T17:00:00-06:00")
               for pid, name, rating, level, games in SAMPLE_PLAYERS}

    print("== Rating Night results ==")
    for g in SAMPLE_GAMES:
        for c in apply_game(g, players):
            print(f"{g.id}  {players[c.member_id].name}: {fmt(c.before)} -> {fmt(c.after)} ({c.delta:+.2f})")

    now = datetime.fromisoformat("2027-01-11T09:00:00-06:00")
    print("\n== Profile field values (written to CourtReserve) ==")
    tiers = ranked_tiers(list(players.values()), epic_size=2)  # only 8 sample players, so top 2 are "Epic"
    for p in players.values():
        rel = reliability(p.member_id, SAMPLE_GAMES, now)
        print(f'{p.name}: "{fmt(p.rating)} · {rel}%" ({reliability_label(rel)}), ranked tier {tiers[p.member_id]}')

    print("\n== Monday level list ==")
    print(format_monday_list(monday_level_list(list(players.values())), players))

    print("\n== Fill report, next 7 days ==")
    rows = fill_report(SAMPLE_EVENTS, now)
    for r in rows:
        flag = f"  <- {r['flag']}" if r["flag"] else ""
        print(f"{r['start'][:16]}  {r['name']}: {r['registered']}/{r['capacity']}{flag}")
    for c in fill_by_category(rows):
        print(f"  {c['category']}: {round(c['fill'] * 100)}% full")

    print("\n== Draft coach pay (group sessions) ==")
    lines, unmatched = coach_pay_sheet(SAMPLE_REGISTRATIONS)
    for l in lines:
        print(f"{l['coach']}: {l['sessions']} sessions, {l['hours']:g} h, ${l['amount']:.2f}")
    if unmatched:
        print("Couldn't match a coach:", ", ".join(unmatched))


if __name__ == "__main__":
    main()
