-- Epic Ops schema. CourtReserve stays the source of truth for members, events and money;
-- these tables hold copies for reports plus the Epic Rating data CourtReserve can't store.

create table members (
  member_id      bigint primary key,           -- CourtReserve OrganizationMemberId
  first_name     text not null,
  last_name      text not null,
  email          text,
  gender         text,
  membership     text,
  status         text,
  dupr           text,                          -- display only, never used for placement
  cr_level       text,                          -- band currently set in CourtReserve
  synced_at      timestamptz not null default now()
);

create table players (
  member_id          bigint primary key references members(member_id),
  rating             numeric(4,2) not null check (rating >= 2.00),
  level              text check (level in ('L1','L2','L3','L4','L5')),
  rated_games        int not null default 0,
  updates_below_band int not null default 0,
  shield_games_left  int not null default 0,
  boosted_games_left int not null default 5,
  last_rated_game_at timestamptz,
  seeded_from        text not null default 'welcome_lesson',
  updated_at         timestamptz not null default now()
);

create table games (
  id         uuid primary key default gen_random_uuid(),
  played_at  timestamptz not null,
  source     text not null check (source in ('rating_night','ranked_court','league','epic_series')),
  team_a     bigint[] not null,
  team_b     bigint[] not null,
  score_a    int not null,
  score_b    int not null,
  entered_by text not null,                    -- court host or coach
  check (score_a <> score_b)
);

create table rating_changes (
  game_id   uuid references games(id) on delete cascade,
  member_id bigint references players(member_id),
  before    numeric(4,2) not null,
  after     numeric(4,2) not null,
  primary key (game_id, member_id)
);

-- Coach appeals: +/-0.15 max per appeal; bigger needs Dillon's sign-off.
create table appeals (
  id          uuid primary key default gen_random_uuid(),
  member_id   bigint references players(member_id),
  coach       text not null,
  change      numeric(3,2) not null,
  reason      text not null,
  approved_by text,
  created_at  timestamptz not null default now(),
  check (abs(change) <= 0.15 or approved_by = 'Dillon')
);

create table events (
  event_id       bigint primary key,
  name           text not null,
  category       text not null,
  starts_at      timestamptz not null,
  ends_at        timestamptz not null,
  max_registrants int,
  registered     int,
  synced_at      timestamptz not null default now()
);

create table registrations (
  event_date_id bigint not null,
  event_id      bigint not null,
  member_id     bigint not null,
  price_to_pay  numeric(8,2),
  paid          numeric(8,2),
  cancelled_at  timestamptz,
  primary key (event_date_id, member_id)
);

-- The sync runs every 10 minutes from GitHub Actions (.github/workflows/sync.yml).
