# Epic Ops

Epic Ops is a companion web app for Epic Pickleball. It's written in Python with Streamlit, and uses Supabase (hosted Postgres) as the database. Members keep using CourtReserve for everything, and Epic Ops does the work CourtReserve can't:

- **Epic Rating and Epic Ranked math.** Each game moves a player 0.01 to 0.06. New players get 5 placement games at double movement, and players back after 3+ months get 3. There's no rank decay.
- **Epic Reliability** (0 to 100%), built from recency, volume and variety of games.
- **Level placement from the Epic Rating alone.** DUPR is for display only. Players move up straight away, but only drop after 2 weekly checks below their band, with a 3-game shield after a promotion.
- **The Monday level list:** who staff need to move to a new band on the CourtReserve "Epic Rating" category.
- **Fill report** (full and under-half-full events, fill by category) and a **draft coach pay sheet**.

All the rules live in `epic_ops/config.py`, so you can change a number in one place.

## The web app

Staff use Epic Ops in a browser, on a laptop or a phone. It has five pages:

| Page | Who uses it | What it does |
| --- | --- | --- |
| Score entry | Court hosts on Rating Night | Pick 4 players and enter the score. Ratings update right away. |
| Ratings | Coaches | Every player's Epic Rating, last move, reliability, level and ranked tier |
| Monday level list | Front desk | Who to move to a new band in CourtReserve, with a Done button for each |
| Fill report | You | Next 7 days: full events (add a section?) and events under half full, by category |
| Coach pay | You | Draft pay per coach, with a CSV download |

It runs on **sample data** for now, so nothing touches CourtReserve, and changes reset when the app restarts.

### Run it on your computer

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
streamlit run app/streamlit_app.py    # opens http://localhost:8501
pytest                                # 38 tests
python -m scripts.demo                # the same loop, printed in the terminal
```

### Put it online (free, on Render)

1. Push this folder to a private GitHub repo (it's `dilly1012/Epic-Ops`).
2. At https://render.com choose **New > Blueprint** and pick the repo. Render reads `render.yaml` (free Python web service, Python 3.12, health check).
3. When asked, set **APP_PASSWORD** to the staff password. It lives only in Render's dashboard, never in git.
4. Share the `onrender.com` link with staff only. The free plan sleeps after 15 minutes idle and takes about a minute to wake, so open it a few minutes before you need it.

Without a password the app is open to anyone with the link, which is only OK on your own computer. Locally, put `app_password = "..."` in `.streamlit/secrets.toml` (git-ignored).

**Why not Streamlit Community Cloud:** we tried it first (Nov 2026). That deployment dropped about 1 in 5 parallel requests, so the page usually hung on a spinner. The app also still pins `streamlit<1.57` and `pyarrow<25` from that attempt. The code still reads `app_password` from Streamlit secrets, so Streamlit Cloud works if you want to retry it.

## Connect to CourtReserve (Phase 1, read only)

1. Check that Epic's CourtReserve plan is Advance, Momentum or Enterprise, since the API needs one of these.
2. Create a key under Settings > Additional Features > Integrations > API Access. Start it **read only**.
3. Create a Supabase project. In its SQL editor, run `supabase/migrations/001_init.sql`.
4. Copy `.env.example` to `.env`, fill it in, load it into your shell, and run `python -m scripts.sync`.
5. Push to GitHub and add the four secrets that `.github/workflows/sync.yml` uses. The sync then runs every 10 minutes for free.

The client refuses all writes unless `CR_WRITE_ENABLED=true`. It also throttles itself under CourtReserve's limit of 60 calls a minute.

## What the CourtReserve API can't do

These come from the public API spec, so confirm them against https://api.courtreserve.com/apihelp/index.

- **No webhooks.** Epic Ops polls every 10 minutes instead.
- **It can't create events.** Staff build each season in the admin.
- **It can't set a member's rating category.** Epic Ops writes the exact number ("3.62") and reliability ("85%") to two custom fields, and staff apply the band from the Monday list.
- **It doesn't return waitlist counts.** A full event is the best signal for adding a second section.

## Conventions it relies on (set up in Phase 0)

- **Event names:** `Category · Level · Coach`, for example `Clinic · L4 · Dillon`. The pay sheet reads the coach from here.
- **Rating category:** a custom one named `Epic Rating`, with options `L1 2.00-2.49` through `L5 4.00+`.
- **Custom fields:** `Epic Rating` (3.62) and `Reliability` (85%). Put their ids in `CR_EPIC_RATING_FIELD_ID` and `CR_RELIABILITY_FIELD_ID`.
- **Leagues and Rating Night:** CourtReserve flex leagues, with players entering scores in the member portal. Each week, export the results to Excel. Importing that export is the next feature. The score entry page is for ranked courts during open play.

## Layout

```
epic_ops/config.py           all rules and numbers
epic_ops/rating/             elo.py (game movement), levels.py (bands, tiers), reliability.py
epic_ops/jobs/               monday_list.py, fill_report.py, coach_pay.py
epic_ops/courtreserve/       API client
epic_ops/store/              Supabase writes
scripts/                     demo.py, sync.py
app/                         Streamlit web app (streamlit_app.py + views/)
epic_ops/state.py            where the web app reads and writes data
supabase/migrations/         SQL schema
```

## Next up

- Save the web app's data to Supabase instead of memory. `epic_ops/state.py` is the one file to swap.
- Writing ratings back to CourtReserve.
- Coach appeals (±0.15, or more with Dillon's sign-off).
- Court blocks for Rating Night waves.
