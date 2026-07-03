"""
xmotion_db.py - One-shot builder for XMotion.db (idempotent).
Implements Analysis/XMotion-DB-Schema.md + the x_factors extension.
Run:  py xmotion_db.py           -> creates/updates C:\\dev\\XMotion\\Analysis\\XMotion.db
      py xmotion_db.py --demo    -> builds a throwaway _demo.db with sample rows (smoke test)
"""
import sqlite3, sys
from pathlib import Path

ANALYSIS = Path(r"C:\dev\XMotion\Analysis")
DEMO = "--demo" in sys.argv
DB = ANALYSIS / ("XMotion_demo.db" if DEMO else "XMotion.db")

DDL = """
CREATE TABLE IF NOT EXISTS vas (
  va_id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, start_date TEXT,
  commission_rate REAL NOT NULL DEFAULT 0.30, status TEXT DEFAULT 'active', skill_notes TEXT);

CREATE TABLE IF NOT EXISTS locations (
  location_id INTEGER PRIMARY KEY, city TEXT, region TEXT, country TEXT,
  market_tier TEXT, notes TEXT, UNIQUE(city, region, country));

CREATE TABLE IF NOT EXISTS listings (
  listing_id INTEGER PRIMARY KEY, date_started TEXT NOT NULL,
  va_id INTEGER REFERENCES vas(va_id), property_link TEXT,
  location_id INTEGER REFERENCES locations(location_id),
  images_n INTEGER, s_per_image REAL,
  duration_raw REAL GENERATED ALWAYS AS (s_per_image * images_n) VIRTUAL,
  duration_rounded INTEGER GENERATED ALWAYS AS
    (MIN(CAST(round(s_per_image * images_n / 5.0) * 5 AS INTEGER), 90)) VIRTUAL,
  ambiguity INTEGER, noise REAL, quality_sd REAL, quality_verdict TEXT,
  model TEXT, shots_used INTEGER DEFAULT 0, shot1_result TEXT, shot2_result TEXT,
  outcome TEXT DEFAULT 'In-Progress', abandon_reason TEXT, notes TEXT,
  created_at TEXT DEFAULT (datetime('now')));

CREATE TABLE IF NOT EXISTS offers (
  offer_id INTEGER PRIMARY KEY,
  listing_id INTEGER NOT NULL REFERENCES listings(listing_id),
  offer_date TEXT, offer_price REAL, offer_result TEXT DEFAULT 'Pending',
  responded_date TEXT,
  revenue REAL GENERATED ALWAYS AS
    (CASE WHEN offer_result='Accepted' THEN offer_price ELSE 0 END) VIRTUAL);

CREATE TABLE IF NOT EXISTS duration_grid (
  images_n INTEGER, s_per_image REAL, duration_rounded INTEGER,
  PRIMARY KEY (images_n, s_per_image));

CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT);

-- X-Factor Relativity extension
CREATE TABLE IF NOT EXISTS x_factors (
  x_factor_id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL,
  category TEXT, description TEXT, created_at TEXT DEFAULT (datetime('now')));

CREATE TABLE IF NOT EXISTS listing_x_factors (
  listing_id INTEGER NOT NULL REFERENCES listings(listing_id),
  x_factor_id INTEGER NOT NULL REFERENCES x_factors(x_factor_id),
  spotted_by TEXT, note TEXT,
  PRIMARY KEY (listing_id, x_factor_id));

-- Overlay template dimension (2026-07-03 expansion)
CREATE TABLE IF NOT EXISTS overlay_templates (
  template_id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL,   -- 'A-1', 'A-2'...
  placement TEXT,            -- center-bottom-right | top-right | ...
  loop_version TEXT,         -- which animated loop build
  created_at TEXT DEFAULT (datetime('now')));

CREATE INDEX IF NOT EXISTS ix_listings_va   ON listings(va_id);
CREATE INDEX IF NOT EXISTS ix_listings_loc  ON listings(location_id);
CREATE INDEX IF NOT EXISTS ix_listings_s    ON listings(s_per_image);
CREATE INDEX IF NOT EXISTS ix_listings_date ON listings(date_started);
CREATE INDEX IF NOT EXISTS ix_offers_listing ON offers(listing_id);
CREATE INDEX IF NOT EXISTS ix_lxf_xf ON listing_x_factors(x_factor_id);
"""

# Idempotent column adds (SQLite has no ADD COLUMN IF NOT EXISTS).
# (table, column, decl)
MIGRATIONS = [
    # -- shot scoring layer (2026-07-03): Potential / Yield / Resonance --
    ("listings", "model_quality_pctile",  "INTEGER"),  # P1-P100
    ("listings", "shot_quantity_pctile",  "INTEGER"),  # P1-P100
    ("listings", "shot_potential",        "REAL"),     # \u2CB1 (Coptic sm omega) = sqrt(MQ x SQ), Before
    ("listings", "output_quality",        "INTEGER"),  # \u2CB0 (Coptic cap omega) = Output Video Quality 1-100, After
    ("listings", "shot_resonance",        "REAL"),     # \u0460 (Cyrillic cap omega) = \u2CB0 (Coptic cap omega) * \u2CB1 (Coptic sm omega), Balanced
    # -- video size / format tracking (handoff directive) --
    ("listings", "frame_aspect",          "TEXT"),     # 16:9 | 9:16 | 1:1
    ("listings", "content_aspect",        "TEXT"),     # e.g. 3:4 when letterboxed
    ("listings", "resolution_out",        "TEXT"),     # e.g. 1080x1920
    ("listings", "border_type",           "TEXT"),     # none | black | white
    ("listings", "overlay_template_id",   "INTEGER REFERENCES overlay_templates(template_id)"),
]

def migrate(cur):
    for tbl, col, decl in MIGRATIONS:
        have = {r[1] for r in cur.execute(f"PRAGMA table_info({tbl})")}
        if col not in have:
            cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {decl}")
            print(f"migrated: {tbl}.{col}")

VIEWS = {
"v_s_performance": """
SELECT l.s_per_image,
  COUNT(DISTINCT l.listing_id) AS listings, COUNT(o.offer_id) AS offers_sent,
  SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate,
  SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END) AS revenue
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
WHERE l.s_per_image IS NOT NULL GROUP BY l.s_per_image""",
"v_duration_performance": """
SELECT l.duration_rounded,
  COUNT(DISTINCT l.listing_id) AS listings, COUNT(o.offer_id) AS offers_sent,
  SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
WHERE l.duration_rounded IS NOT NULL GROUP BY l.duration_rounded""",
"v_grid_cell": """
SELECT l.images_n, l.s_per_image, l.duration_rounded,
  COUNT(DISTINCT l.listing_id) AS listings, COUNT(o.offer_id) AS offers_sent,
  SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
WHERE l.images_n IS NOT NULL GROUP BY l.images_n, l.s_per_image""",
"v_va_scorecard": """
SELECT v.va_id, v.name,
  COUNT(DISTINCT l.listing_id) AS listings, SUM(l.shots_used) AS shots_used,
  ROUND(1.0*SUM(l.shots_used)/NULLIF(COUNT(DISTINCT l.listing_id),0),2) AS avg_shots,
  ROUND(1.0*SUM(l.outcome='Abandoned')/NULLIF(COUNT(DISTINCT l.listing_id),0),3) AS abandon_rate,
  ROUND(AVG(l.quality_sd),2) AS avg_quality_sd,
  COUNT(o.offer_id) AS offers_sent, SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate,
  SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END) AS revenue,
  ROUND(SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END)*v.commission_rate,2) AS commission
FROM vas v LEFT JOIN listings l ON l.va_id=v.va_id
LEFT JOIN offers o ON o.listing_id=l.listing_id GROUP BY v.va_id, v.name""",
"v_location_performance": """
SELECT loc.location_id, loc.city, loc.region, loc.country, loc.market_tier,
  COUNT(DISTINCT l.listing_id) AS listings, ROUND(AVG(l.quality_sd),2) AS avg_quality_sd,
  COUNT(o.offer_id) AS offers_sent, SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate,
  SUM(CASE WHEN o.offer_result='Accepted' THEN o.offer_price ELSE 0 END) AS revenue
FROM locations loc LEFT JOIN listings l ON l.location_id=loc.location_id
LEFT JOIN offers o ON o.listing_id=l.listing_id GROUP BY loc.location_id""",
"v_quality_vs_outcome": """
SELECT l.quality_verdict, COUNT(*) AS listings, COUNT(o.offer_id) AS offers_sent,
  SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
WHERE l.quality_verdict IS NOT NULL GROUP BY l.quality_verdict""",
"v_monthly_ops": """
SELECT substr(l.date_started,1,7) AS month,
  COUNT(DISTINCT l.listing_id) AS listings, SUM(l.shots_used) AS shots_used,
  ROUND(1.0*SUM(l.outcome='Abandoned')/NULLIF(COUNT(DISTINCT l.listing_id),0),3) AS abandon_rate
FROM listings l GROUP BY substr(l.date_started,1,7)""",
"v_shot_scoring": """
SELECT l.listing_id, l.date_started, v.name AS va, l.model,
  l.model_quality_pctile, l.shot_quantity_pctile,
  l.shot_potential, l.output_quality, l.shot_resonance,
  l.quality_sd, l.quality_verdict, l.outcome
FROM listings l LEFT JOIN vas v ON v.va_id=l.va_id
WHERE l.shot_potential IS NOT NULL OR l.output_quality IS NOT NULL""",
"v_va_shot_scoring": """
SELECT v.va_id, v.name,
  COUNT(l.listing_id) AS scored_shots,
  ROUND(AVG(l.shot_potential),1)  AS avg_potential,
  ROUND(AVG(l.output_quality),1)  AS avg_yield,
  ROUND(AVG(l.shot_resonance),0)  AS avg_resonance,
  ROUND(AVG(l.quality_sd),2)      AS avg_sd
FROM vas v JOIN listings l ON l.va_id=v.va_id
WHERE l.output_quality IS NOT NULL GROUP BY v.va_id, v.name""",
"v_model_scoring": """
SELECT l.model,
  COUNT(l.listing_id) AS scored_shots,
  ROUND(AVG(l.shot_potential),1)  AS avg_potential,
  ROUND(AVG(l.output_quality),1)  AS avg_yield,
  ROUND(AVG(l.shot_resonance),0)  AS avg_resonance
FROM listings l WHERE l.model IS NOT NULL AND l.output_quality IS NOT NULL
GROUP BY l.model""",
"v_format_combo": """
SELECT l.frame_aspect, l.content_aspect, l.border_type,
  COUNT(DISTINCT l.listing_id) AS listings, COUNT(o.offer_id) AS offers_sent,
  SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM listings l LEFT JOIN offers o ON o.listing_id=l.listing_id
WHERE l.frame_aspect IS NOT NULL GROUP BY l.frame_aspect, l.content_aspect, l.border_type""",
"v_overlay_performance": """
SELECT t.template_id, t.name, t.placement, t.loop_version,
  COUNT(DISTINCT l.listing_id) AS listings, COUNT(o.offer_id) AS offers_sent,
  SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM overlay_templates t
LEFT JOIN listings l ON l.overlay_template_id=t.template_id
LEFT JOIN offers o ON o.listing_id=l.listing_id
GROUP BY t.template_id, t.name""",
"v_x_factor_performance": """
SELECT xf.x_factor_id, xf.name, xf.category,
  COUNT(DISTINCT lx.listing_id) AS listings,
  COUNT(o.offer_id) AS offers_sent, SUM(o.offer_result='Accepted') AS accepted,
  ROUND(1.0*SUM(o.offer_result='Accepted')/NULLIF(COUNT(o.offer_id),0),3) AS conversion_rate
FROM x_factors xf
LEFT JOIN listing_x_factors lx ON lx.x_factor_id=xf.x_factor_id
LEFT JOIN listings l ON l.listing_id=lx.listing_id
LEFT JOIN offers o ON o.listing_id=l.listing_id
GROUP BY xf.x_factor_id, xf.name""",
}

GRID = [(n, s) for n in (5, 8, 10, 12, 15, 18, 20, 25) for s in (2.0, 2.5, 3.0, 4.0)]

CONFIG = [
    ("s_rotation", "2.0,2.5,3.0,4.0"), ("s_next_index", "0"), ("s_locked", ""),
    ("lock_threshold_offers", "20"), ("rollup_every_offers", "10"),
]

def main():
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript(DDL)
    migrate(cur)
    for name, body in VIEWS.items():
        cur.execute(f"DROP VIEW IF EXISTS {name}")
        cur.execute(f"CREATE VIEW {name} AS {body}")
    for n, s in GRID:
        d = min(round(n * s / 5) * 5, 90)
        cur.execute("INSERT OR IGNORE INTO duration_grid VALUES (?,?,?)", (n, s, int(d)))
    for k, v in CONFIG:
        cur.execute("INSERT OR IGNORE INTO config VALUES (?,?,datetime('now'))", (k, v))
    for va in ("Jaisa", "Richlan"):
        cur.execute("INSERT OR IGNORE INTO vas (name, start_date) VALUES (?, date('now'))", (va,))

    cur.execute("INSERT OR IGNORE INTO overlay_templates (name, placement, loop_version) VALUES "
                "('A-1','center-bottom-right','loop-v1'),('A-2','top-right','loop-v1')")

    if DEMO:
        import math, random
        random.seed(9)
        cur.execute("INSERT OR IGNORE INTO locations (city,region,country,market_tier) VALUES "
                    "('Austin','TX','US','tier-1'),('Cebu','Central Visayas','PH','tier-2'),"
                    "('Miami','FL','US','tier-1')")
        for i in range(24):
            n = random.choice((8, 10, 12, 15, 18, 20))
            s = random.choice((2.0, 2.5, 3.0, 4.0))
            amb = random.choice((1, 2, 2, 4))
            noi = random.choice((1, 2, 2, 3))
            sd = round(math.sqrt(amb * noi), 2)
            verdict = "PASS" if sd <= 2.0 else ("MAYBE" if sd <= 3.5 else "FAIL")
            mq = random.choice((55, 70, 85, 92))
            sq = random.choice((40, 60, 75, 90))
            pot = round(math.sqrt(mq * sq), 1)
            yld = random.randint(45, 96)
            reso = round(pot * yld)
            fa = random.choice(("16:9", "9:16", "9:16", "1:1"))
            ca = "3:4" if fa == "9:16" and random.random() < 0.6 else fa
            bt = "none" if ca == fa else random.choice(("black", "white"))
            cur.execute("INSERT INTO listings (date_started,va_id,location_id,images_n,s_per_image,"
                        "ambiguity,noise,quality_sd,quality_verdict,shots_used,shot1_result,outcome,"
                        "model,model_quality_pctile,shot_quantity_pctile,shot_potential,"
                        "output_quality,shot_resonance,frame_aspect,content_aspect,border_type,"
                        "overlay_template_id) "
                        "VALUES (date('now','-'||?||' days'),?,?,?,?,?,?,?,?,1,'S','Sent',"
                        "?,?,?,?,?,?,?,?,?,?)",
                        (i, 1 + i % 2, 1 + i % 3, n, s, amb, noi, sd, verdict,
                         random.choice(("kling3_0", "seedance_2_0", "minimax")), mq, sq, pot,
                         yld, reso, fa, ca, bt, 1 + i % 2))
            lid = cur.lastrowid
            res = random.choice(("Accepted", "Declined", "No-Reply", "Pending"))
            cur.execute("INSERT INTO offers (listing_id,offer_date,offer_price,offer_result) "
                        "VALUES (?,date('now'),?,?)", (lid, random.choice((295, 395)), res))

    con.commit()
    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    views = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    grid_n = cur.execute("SELECT COUNT(*) FROM duration_grid").fetchone()[0]
    print(f"DB: {DB}")
    print(f"tables: {tables}")
    print(f"views:  {views}")
    print(f"duration_grid cells: {grid_n} (expect 32)")
    con.close()

if __name__ == "__main__":
    main()
