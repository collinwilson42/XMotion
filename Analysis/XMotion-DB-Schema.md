---
name: XMotion Analytics DB
description: The single-source analytics database schema for XMotion. Use when creating, querying, or extending the XMotion database — logging listings, VA shot quantity, internal quality (SD) scores, S-value/duration grid analytics, location performance, and offers/commission. One SQLite file, star schema, analytics as views. Defines the N / S / S*N grid and the canonical rounding formula.
tools: filesystem
type: schema
domain: analytics
status: draft
version: 0.2
updated: 2026-07-03
db_path: C:\dev\XMotion\Analysis\XMotion.db
maintainer: XMotion Studio
signed: wiz-4 (Head of Development)
growth:
  - Ship _Tools/xmotion_db.py bootstrap and smoke-test into a live XMotion.db
  - Decide re-offer conversion policy (first-offer-only vs any-accept)
  - Seed locations from Location Tracking and Notes when formalized
  - Optional 3.5 s-per-image band if finer pacing resolution is wanted
---

# XMotion Analytics Database — Full-Scope Schema Outline

> **One database, all analysis.** A single SQLite file at `C:\dev\XMotion\Analysis\XMotion.db`
> is the canonical store for every metric: location tracking, per-VA shot quantity,
> internal quality (SD) scores, the S-value / duration grid, and offer/commission
> outcomes. Facts live in one table; people and place are dimensions; analytics are
> **views** so the raw data is never denormalized for reporting. The old
> `Master_Tracking_Log.csv` becomes an export mirror, not the source of truth.

---

## 0. Why SQLite + star schema (not a wide CSV)

A wide CSV can *record* but it can't *slice* — you can't cleanly ask "conversion by S-value, controlled for VA and location" in a flat file. A star schema (one fact table, small dimensions, analytics as views) gives real multi-axis analytics while staying a single portable file X reads/writes over the filesystem MCP. VAs never touch SQL; X does the reads/writes and reports, exactly as it does with the CSV today.

---

## 1. Core lever definitions (terminology lock)

- **N** — image count for the listing.
- **S** — **seconds per image** (the pacing lever): `2.0 / 2.5 / 3.0 / 4.0`.
- **duration_raw** — `S * N` (exact seconds).
- **duration_rounded** — `MIN( round(S*N / 5) * 5, 90 )` — nearest 5s, capped at 90.
  - Rounding is **half-away-from-zero** (SQLite `round()` semantics). **Verified against all 32 grid cells — zero mismatches**, including the 12.5→15 and 62.5→65 ties.

> **Terminology note.** Earlier docs used "S value" for *total* duration (10–60s) and rotated those. In this DB, **S = seconds per image** and total duration is derived (`S*N`). This is the analytically stronger lever because it normalizes pacing across listings with different N. The old total-duration rotation is now just `duration_rounded`.

---

## 2. Entity overview

```
        vas ──────┐                 ┌────── locations
                  │                 │
                  ▼                 ▼
               ┌──────────────────────┐        ┌──────────────┐
               │       listings       │───────<│    offers     │
               │  (one row / attempt) │        │ (0..n / list) │
               └──────────────────────┘        └──────────────┘
                          │
                          ▼ (lookup)
                   duration_grid (reference 8×4)
                   config (rotation / lock state)
```

- **listings** — the fact table (one row per property attempt).
- **vas** — the two operators (Jaisa, Richlan), extensible.
- **locations** — market/location tracking dimension.
- **offers** — the sales side (usually 1 per Sent listing; table allows re-offers).
- **duration_grid** — materialized N×S → duration reference (the default grid).
- **config** — rotation index / locked-S / thresholds (key-value).

---

## 3. Table specifications (DDL)

### 3.1 vas
```sql
CREATE TABLE vas (
  va_id           INTEGER PRIMARY KEY,
  name            TEXT UNIQUE NOT NULL,          -- 'Jaisa', 'Richlan'
  start_date      TEXT,                          -- ISO date
  commission_rate REAL NOT NULL DEFAULT 0.30,    -- 30%
  status          TEXT DEFAULT 'active',         -- onboarding | active | paused
  skill_notes     TEXT                           -- what they're working to improve
);
```

### 3.2 locations
```sql
CREATE TABLE locations (
  location_id  INTEGER PRIMARY KEY,
  city         TEXT,
  region       TEXT,                             -- state / province
  country      TEXT,
  market_tier  TEXT,                             -- tier-1 | tier-2 | tier-3
  notes        TEXT,                             -- from Location Tracking & Notes
  UNIQUE(city, region, country)
);
```

### 3.3 listings  (fact)
```sql
CREATE TABLE listings (
  listing_id       INTEGER PRIMARY KEY,
  date_started     TEXT NOT NULL,                -- ISO date
  va_id            INTEGER REFERENCES vas(va_id),
  property_link    TEXT,
  location_id      INTEGER REFERENCES locations(location_id),

  -- the grid
  images_n         INTEGER,                      -- N
  s_per_image      REAL,                         -- S  (2.0/2.5/3.0/4.0)
  duration_raw     REAL GENERATED ALWAYS AS (s_per_image * images_n) VIRTUAL,
  duration_rounded INTEGER GENERATED ALWAYS AS
                     (MIN(CAST(round(s_per_image * images_n / 5.0) * 5 AS INTEGER), 90)) VIRTUAL,

  -- internal quality (Shot Quality Equation, SD side)
  ambiguity        INTEGER,                      -- 1/2/4/8/16
  noise            REAL,                         -- 1..5
  quality_sd       REAL,                         -- sqrt(ambiguity*noise); X computes on insert
  quality_verdict  TEXT,                         -- PASS | MAYBE | FAIL

  -- production
  model            TEXT,                         -- Higgsfield model
  shots_used       INTEGER DEFAULT 0,            -- 1 or 2 (Two-Shot Rule)
  shot1_result     TEXT,                         -- S | F
  shot2_result     TEXT,                         -- S | F | NULL
  outcome          TEXT DEFAULT 'In-Progress',   -- In-Progress | Sent | Abandoned
  abandon_reason   TEXT,                          -- Low-Res | Fisheye | Odd-Angles | Too-Few | Lighting | Clutter | Ambiguity
  notes            TEXT,
  created_at       TEXT DEFAULT (datetime('now'))
);
```
> `quality_sd` is stored (not generated) so the schema doesn't depend on SQLite math
> functions being compiled in — X computes `sqrt(ambiguity*noise)` at insert. The two
> duration columns use only `round()`, which is always available.

### 3.4 offers
```sql
CREATE TABLE offers (
  offer_id       INTEGER PRIMARY KEY,
  listing_id     INTEGER NOT NULL REFERENCES listings(listing_id),
  offer_date     TEXT,
  offer_price    REAL,                           -- 295 | 395
  offer_result   TEXT DEFAULT 'Pending',         -- Pending | Accepted | Declined | No-Reply
  responded_date TEXT,
  revenue        REAL GENERATED ALWAYS AS
                   (CASE WHEN offer_result='Accepted' THEN offer_price ELSE 0 END) VIRTUAL
);
```
> Commission depends on the VA's rate, so it's computed in `v_va_scorecard` (a join),
> not stored here — keeps a rate change from silently desyncing historical rows.

### 3.5 duration_grid  (reference — the default grid, materialized)
```sql
CREATE TABLE duration_grid (
  images_n         INTEGER,
  s_per_image      REAL,
  duration_rounded INTEGER,
  PRIMARY KEY (images_n, s_per_image)
);
```
Seed (all 32 cells — matches your table exactly):
```sql
INSERT INTO duration_grid (images_n, s_per_image, duration_rounded) VALUES
 (5,2.0,10),(5,2.5,15),(5,3.0,15),(5,4.0,20),
 (8,2.0,15),(8,2.5,20),(8,3.0,25),(8,4.0,30),
 (10,2.0,20),(10,2.5,25),(10,3.0,30),(10,4.0,40),
 (12,2.0,25),(12,2.5,30),(12,3.0,35),(12,4.0,50),
 (15,2.0,30),(15,2.5,40),(15,3.0,45),(15,4.0,60),
 (18,2.0,35),(18,2.5,45),(18,3.0,55),(18,4.0,70),
 (20,2.0,40),(20,2.5,50),(20,3.0,60),(20,4.0,80),
 (25,2.0,50),(25,2.5,65),(25,3.0,75),(25,4.0,90);
```

### 3.6 config  (rotation / lock state)
```sql
CREATE TABLE config (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT);
INSERT INTO config (key,value,updated_at) VALUES
 ('s_rotation','2.0,2.5,3.0,4.0', datetime('now')),
 ('s_next_index','0',             datetime('now')),  -- rotate S across listings
 ('s_locked','',                  datetime('now')),  -- set after threshold if a winner emerges
 ('lock_threshold_offers','20',   datetime('now')),  -- lock best S after N offers
 ('rollup_every_offers','10',     datetime('now'));  -- recompute S table every N offers
```

### 3.7 indexes
```sql
CREATE INDEX ix_listings_va       ON listings(va_id);
CREATE INDEX ix_listings_loc      ON listings(location_id);
CREATE INDEX ix_listings_s        ON listings(s_per_image);
CREATE INDEX ix_listings_date     ON listings(date_started);
CREATE INDEX ix_offers_listing    ON offers(listing_id);
```

---

## 4. Analytics views (the "run proper analytics on the grid" layer)

### 4.1 S-value performance (the headline)
```sql
CREATE VIEW v_s_performance AS
SELECT l.s_per_image,
       COUNT(DISTINCT l.listing_id)                                   AS listings,
       COUNT(o.offer_id)                                              AS offers_sent,
       SUM(o.offer_result='Accepted')                                 AS accepted,
       ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate,
       SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END)  AS revenue
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
GROUP BY l.s_per_image;
```

### 4.2 Duration-bucket performance (the S*N output side)
```sql
CREATE VIEW v_duration_performance AS
SELECT l.duration_rounded,
       COUNT(DISTINCT l.listing_id)                                   AS listings,
       COUNT(o.offer_id)                                              AS offers_sent,
       SUM(o.offer_result='Accepted')                                 AS accepted,
       ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
GROUP BY l.duration_rounded;
```

### 4.3 Grid cell (N × S) — for when data is dense enough
```sql
CREATE VIEW v_grid_cell AS
SELECT l.images_n, l.s_per_image, l.duration_rounded,
       COUNT(DISTINCT l.listing_id)                                   AS listings,
       COUNT(o.offer_id)                                              AS offers_sent,
       SUM(o.offer_result='Accepted')                                 AS accepted,
       ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
GROUP BY l.images_n, l.s_per_image;
```

### 4.4 Per-VA scorecard (shot quantity + quality + commission)
```sql
CREATE VIEW v_va_scorecard AS
SELECT v.va_id, v.name,
       COUNT(DISTINCT l.listing_id)                                   AS listings,
       SUM(l.shots_used)                                              AS shots_used,
       ROUND(1.0*SUM(l.shots_used)/NULLIF(COUNT(DISTINCT l.listing_id),0),2) AS avg_shots,
       ROUND(1.0*SUM(l.outcome='Abandoned')/NULLIF(COUNT(DISTINCT l.listing_id),0),3) AS abandon_rate,
       ROUND(AVG(l.quality_sd),2)                                     AS avg_quality_sd,
       COUNT(o.offer_id)                                              AS offers_sent,
       SUM(o.offer_result='Accepted')                                 AS accepted,
       ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate,
       SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END)  AS revenue,
       ROUND(SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END)*v.commission_rate,2) AS commission
FROM vas v
LEFT JOIN listings l ON l.va_id=v.va_id
LEFT JOIN offers  o ON o.listing_id=l.listing_id
GROUP BY v.va_id, v.name;
```

### 4.5 Location performance
```sql
CREATE VIEW v_location_performance AS
SELECT loc.location_id, loc.city, loc.region, loc.country, loc.market_tier,
       COUNT(DISTINCT l.listing_id)                                   AS listings,
       ROUND(AVG(l.quality_sd),2)                                     AS avg_quality_sd,
       COUNT(o.offer_id)                                              AS offers_sent,
       SUM(o.offer_result='Accepted')                                 AS accepted,
       ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate,
       SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END)  AS revenue
FROM locations loc
LEFT JOIN listings l ON l.location_id=loc.location_id
LEFT JOIN offers  o ON o.listing_id=l.listing_id
GROUP BY loc.location_id;
```

### 4.6 Quality → outcome (does the gate predict conversion?)
```sql
CREATE VIEW v_quality_vs_outcome AS
SELECT l.quality_verdict,
       COUNT(*)                                                       AS listings,
       COUNT(o.offer_id)                                              AS offers_sent,
       SUM(o.offer_result='Accepted')                                 AS accepted,
       ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
GROUP BY l.quality_verdict;
```

### 4.7 Monthly ops (capacity + abandonment guardrails)
```sql
CREATE VIEW v_monthly_ops AS
SELECT substr(l.date_started,1,7)                                     AS month,
       COUNT(DISTINCT l.listing_id)                                   AS listings,
       SUM(l.shots_used)                                              AS shots_used,   -- vs 60–100 plan cap
       ROUND(1.0*SUM(l.outcome='Abandoned')/NULLIF(COUNT(DISTINCT l.listing_id),0),3) AS abandon_rate  -- flag > 0.20
FROM listings l
GROUP BY substr(l.date_started,1,7);
```

---

## 5. Autonomous write triggers (maps to WBS Segment 5)

X performs these DB ops as reflexes, unprompted:

| Lifecycle moment | DB operation |
|---|---|
| VA starts a listing | `INSERT INTO listings` (date, va, link, location, N, S from rotation), `outcome='In-Progress'` |
| Shot 1 result | `UPDATE listings SET shot1_result=?, shots_used=1` |
| Shot 2 (if needed) | `UPDATE listings SET shot2_result=?, shots_used=2` |
| Quality scored | `UPDATE listings SET ambiguity=?, noise=?, quality_sd=?, quality_verdict=?` |
| Offer sent | `UPDATE listings SET outcome='Sent'` + `INSERT INTO offers` (date, price) |
| Offer result | `UPDATE offers SET offer_result=?, responded_date=?` |
| Abandoned | `UPDATE listings SET outcome='Abandoned', abandon_reason=?` |
| Every 10 offers | report `v_s_performance` (rollup) |
| After 20 offers | if a clear winner, `UPDATE config SET value=? WHERE key='s_locked'` |

Rotation: read `config.s_next_index`, assign `s_rotation[index]`, advance index — unless `s_locked` is set, then use it.

---

## 6. Migration from Master_Tracking_Log.csv

| CSV column | New home |
|---|---|
| Date | `listings.date_started` |
| VA Name | `vas.name` → `listings.va_id` |
| Property Link | `listings.property_link` |
| Images (N) | `listings.images_n` |
| S Value | `listings.s_per_image` *(re-express old total-S as per-image = totalS/N; or backfill from grid)* |
| Shot 1 / Shot 2 | `listings.shot1_result` / `shot2_result` |
| Outcome | `listings.outcome` |
| Offer Date / Price | `offers.offer_date` / `offer_price` |
| Offer Result | `offers.offer_result` |
| Revenue | derived (`offers.revenue`) |
| Commission | derived (`v_va_scorecard`) |
| Abandon Reason | `listings.abandon_reason` |
| Model | `listings.model` |
| Notes | `listings.notes` |

The CSV can be regenerated any time as a flat export view for quick eyeballing — the DB stays canonical.

---

## 7. Bootstrap

Recommended: a one-shot builder `_Tools\xmotion_db.py` that runs all the DDL above, seeds `duration_grid` + `config` + the two VAs, and is idempotent (`CREATE TABLE IF NOT EXISTS`). Then X only ever does row-level reads/writes. *(Say the word and I'll ship that script — it's ~60 lines and I can smoke-test it end to end.)*

---

## 8. Open calibration items

- **S rotation set** — locked to `2.0/2.5/3.0/4.0` per image. Add `3.5` if we want finer pacing resolution later.
- **Quality math** — `quality_sd` stored on insert to stay portable; switch to a generated column only if we confirm math functions are compiled into the bundled SQLite.
- **Re-offers** — `offers` allows multiple per listing (follow-ups). Decide whether conversion counts first-offer-only or any-accept.
- **Location source** — seed `locations` from `Analysis\Location Tracking & Notes` when that reference is formalized.

---

---

## 9. Extension — 2026-07-03 (shot scoring + format/overlay tracking)

**Live in `_Tools\xmotion_db.py` via the idempotent `MIGRATIONS` list; verified against production and demo DBs.**

### 9.1 New columns on `listings`

| Column | Type | Meaning |
|---|---|---|
| `model_quality_pctile` | INTEGER | P1–P100, walkthrough-realism ceiling of the chosen model |
| `shot_quantity_pctile` | INTEGER | P1–P100, credit efficiency at target settings |
| `shot_potential` | REAL | **ⲱ** = √(MQ × SQ) — *Shot Potential (Before)*; X computes at write |
| `output_quality` | INTEGER | **Ⲱ** = Output Video Quality 1–100 — *Shot Yield (After)*; judged on the render |
| `shot_resonance` | REAL | **Ѡ** = Ⲱ × ⲱ — *Shot Resonance (Balanced)*; X computes at write |
| `frame_aspect` | TEXT | 16:9 \| 9:16 \| 1:1 — deliverable frame |
| `content_aspect` | TEXT | actual content aspect (e.g. 3:4 letterboxed inside 9:16) |
| `resolution_out` | TEXT | output resolution, e.g. 1080x1920 |
| `border_type` | TEXT | none \| black \| white |
| `overlay_template_id` | INTEGER | FK → `overlay_templates` |

### 9.2 New dimension: `overlay_templates`

`template_id · name (A-1, A-2…) · placement · loop_version · created_at` — seeded with
A-1 (center-bottom-right) and A-2 (top-right) on loop-v1.

### 9.3 New views

`v_shot_scoring` (per-shot ledger) · `v_va_shot_scoring` (per-VA avg ⲱ/Ⲱ/Ѡ) ·
`v_model_scoring` (per-model avg — the WBS 4.3 ranking table) · `v_format_combo`
(conversion by frame × content × border) · `v_overlay_performance` (conversion by
A-series template).

### 9.4 New dashboards

`Analysis\Shot Scoring` and `Analysis\Format & Overlay` (materializer now projects 6 pages).

### 9.5 Trigger table superseded

§5 remains accurate but is no longer canonical — the complete reflex map including
the scoring and format triggers lives in **`AI Skills\XMotion-Automated-Tracking.md`**.

*Extension signed — wiz-6 (Head of Strategy).*

---

## 10. Extension — 2026-07-03 (sourcing metrics, Collin directive)

**Live in `_Tools\xmotion_db.py` via `MIGRATIONS`; first populated by
`_Tools\xmotion_write_2026-07-03_austin.py` (first live sourcing batch, Austin TX).**

### 10.1 New columns on `listings`

| Column | Type | Meaning |
|---|---|---|
| `price_per_night` | REAL | Airbnb trip price per night incl. fees (USD) at sourcing time |
| `rating` | REAL | listing star rating at sourcing time, e.g. 4.98 |
| `reviews_n` | INTEGER | review count at sourcing time |

Captured at T1 (listing start) when available; backfill permitted as a last-line
correction if sourced after insert. These are candidate predictors for the
Segment-9 prediction model (owner responsiveness / listing maturity signals)
alongside `images_n`, flow read, and `market_tier`.

*Extension recorded — WIZX (Operational & Protocol Leader).*

---

## 11. Extension — 2026-07-04 (Week 2: shot layer + credit budgets)

**Live in `_Tools\xmotion_db.py` (DDL + seed) and applied to production and demo DBs
2026-07-04. Full operating contract: `Onboarding\Week 2 - Production & Distribution.md`.**

### 11.1 New table: `shots` (per-preview-shot ledger — the tier economy is per-shot)

| Column | Type | Meaning |
|---|---|---|
| `shot_id` | INTEGER PK | |
| `listing_id` | INTEGER FK | optional link to `listings` |
| `va_id` | INTEGER FK NOT NULL | producer (Collin has an attribution row) |
| `date_produced` | TEXT NOT NULL | |
| `tier` | TEXT NOT NULL | Tier-1A \| Tier-1B \| Tier-2A \| Tier-2B \| Tier-3A |
| `job_ids` | TEXT | comma-joined Higgsfield job UUIDs incl. regens |
| `credits_used` | REAL | **🔗** total credits to viable shot, incl. regens |
| `quality_ai` | INTEGER | **֎🇦🇮** AI percentile 1–99, post-edit, pending review |
| `quality_final` | INTEGER | **֎** Collin-adjusted 1–99; NULL until reviewed |
| `response_score` | INTEGER | **✔️** 1–99, anchored (1/20/40/60/80/99) |
| `sent_date`, `status` | TEXT | draft \| viable \| sent \| responded \| closed |
| `file_path` | TEXT | materialized filename in `Analytics\Shots` |

**⚡ = √(quality_eff × ✔️) / 🔗** is *not stored* — computed by the materializer
(quality_eff = final when present, else AI); compared within tier only.

### 11.2 New table: `budget_allocations`

`(month 'YYYY-MM', va_id, credits_allocated)` PK (month, va_id). July 2026 seed
(rev 2, upsert): Collin 459.0 · Jaisa 229.5 · Richlan 229.5 (basis 1,147.5; 20%
house reserve is the unallocated remainder — buffer / partner / ⚡ raise).

### 11.3 New column + config

`vas.initials` (TEXT) — filename token; falls back to `upper(substr(name,1,2))`
until real initials are set. `config.filename_glyphs` = on \| off (ASCII QA/QF-V-C-E
fallback for the 🇦🇮 token).

### 11.4 New views

`v_shot_efficiency` (per-shot ledger + review_state, glyph-filename source) ·
`v_budget_status` (allocated/spent/remaining per month × producer) · `v_tier_ab`
(response rate + avg ✔️/֎/credits per tier — the A/B readout).

### 11.5 Dashboard reorganization (2026-07-04)

`Analysis\Shot Quality` and `Analysis\Shot Scoring` are **retired**, merged into
**`Analysis\Shot Quality Scoring`** — the single scoring master covering the full
ladder: SD gate → ⲱ/Ⲱ/Ѡ → ֎/✔️/🔗/⚡ ablation + review queue + monthly ops.
`Analysis\Production & Distribution` is trimmed to budgets + tier A/B outreach only.
The materializer still projects 6 dashboards. Shot filenames in `Analytics\Shots`
are rematerialized from DB truth on every run:
`{YYYY-MM-DD}-{Initials}-{Tier}-֎🇦🇮{q}|֎{q}-✔️{r}-🔗{c}-⚡{e}.mp4`.

### 11.6 New triggers

T14 (shot viable → INSERT) · T15 (֎🇦🇮 post-edit) · T16 (֎ final) · T17 (sent) ·
T18 (✔️ response) · T-B (pre-generation budget check on `v_budget_status`).
Canonical reflex map: `AI Skills\XMotion-Automated-Tracking.md` v1.1.

*Extension signed — wiz-4 (Head of Development), Fable session 2026-07-04.*

---

*Signed — wiz-4 (Head of Development). Schema is buildable as written; §7 turns it into a live DB on command.*
