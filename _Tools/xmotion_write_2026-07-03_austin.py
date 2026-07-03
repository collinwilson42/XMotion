"""
xmotion_write_2026-07-03_austin.py — WIZX batch write, first live sourcing run.
Records the three Austin TX candidates (T1 listing start + T2 quality score +
T11 X-Factors), then runs the materializer (T-all rule).

Idempotent: safe to re-run — listings are keyed on canonical property_link.
Run:  py C:\\dev\\XMotion\\_Tools\\xmotion_write_2026-07-03_austin.py
"""
import sqlite3, subprocess, sys, math
from pathlib import Path

TOOLS = Path(r"C:\dev\XMotion\_Tools")
DB = Path(r"C:\dev\XMotion\Analysis\XMotion.db")

# --- new sourcing-metric columns (also registered in xmotion_db.py MIGRATIONS) ---
NEW_COLS = [
    ("listings", "price_per_night", "REAL"),
    ("listings", "rating", "REAL"),
    ("listings", "reviews_n", "INTEGER"),
]

# --- the batch (scored by WIZX, 2026-07-03, locked scale: Amb 1/2/4/8/16 x Noise 1-5) ---
DATE = "2026-07-03"
LISTINGS = [
    dict(
        link="https://www.airbnb.com/rooms/1522880856219621951",
        block=r"2026-07-03\PM_5-19_5-29",
        images_n=66,           # 67 captured - frame 067 (map/plan, LOW-RES, overlap dup)
        ambiguity=2, noise=1.7,
        price_per_night=337.0, rating=4.98, reviews_n=48,
        notes="Block PM_5-19_5-29. Prep: drop 067 (map, LOW-RES, dup of next block 001); "
              "dedup redundant angles before shot. Collin: strong walkthrough camera-angle potential.",
        x_factor=("Multi-Angle Room Coverage", "property",
                  "Multiple angles per room enable continuous walkthrough camera moves."),
    ),
    dict(
        link="https://www.airbnb.com/rooms/630624331006655039",
        block=r"2026-07-03\PM_5-25_5-35",
        images_n=44,           # 45 captured - frame 001 (map/plan, LOW-RES, dup of prior block 067)
        ambiguity=2, noise=1.7,
        price_per_night=None, rating=None, reviews_n=None,
        notes="Block PM_5-25_5-35. Prep: drop 001 (overlap dup); decide handling of two "
              "1440x1800 portrait frames (016/018) - hold as B-roll or crop for 16:9. "
              "Collin: rooms visibly connect, low ambiguity.",
        x_factor=("Legible Room Flow", "property",
                  "Gallery reads room-to-room; spatial flow is reconstructable at a glance."),
    ),
    dict(
        link="https://www.airbnb.com/rooms/1718466620893746332",
        block=r"2026-07-03\PM_5-30_5-40",
        images_n=55,
        ambiguity=1, noise=1.7,
        price_per_night=None, rating=None, reviews_n=None,
        notes="Block PM_5-30_5-40. Cleanest set of the batch - uniform 1440x960, zero flags, "
              "coherent flow. Listing marked NEW on Airbnb.",
        x_factor=("New-Listing Host Motivation", "market",
                  "Brand-new listings have zero marketing momentum; hosts most receptive to offers."),
    ),
]

def verdict(sd):
    return "PASS" if sd <= 2.0 else ("MAYBE" if sd <= 3.5 else "FAIL")

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 0. defensive migration (idempotent, mirrors xmotion_db.py)
    for tbl, col, decl in NEW_COLS:
        have = {r[1] for r in cur.execute(f"PRAGMA table_info({tbl})")}
        if col not in have:
            cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {decl}")
            print(f"migrated: {tbl}.{col}")

    # 1. ensure location + sourcing attribution row
    cur.execute("INSERT OR IGNORE INTO locations (city,region,country,market_tier) "
                "VALUES ('Austin','TX','US','tier-1')")
    loc_id = cur.execute("SELECT location_id FROM locations WHERE city='Austin' "
                         "AND region='TX' AND country='US'").fetchone()[0]
    cur.execute("INSERT OR IGNORE INTO vas (name, start_date, commission_rate, status, skill_notes) "
                "VALUES ('Collin', ?, 0.0, 'founder', 'Founder - sourcing attribution row, no commission')",
                (DATE,))
    va_id = cur.execute("SELECT va_id FROM vas WHERE name='Collin'").fetchone()[0]

    # 2. S rotation state (T1 detail, tracking skill section 3)
    s_locked = cur.execute("SELECT value FROM config WHERE key='s_locked'").fetchone()[0]
    rotation = [float(x) for x in cur.execute(
        "SELECT value FROM config WHERE key='s_rotation'").fetchone()[0].split(",")]
    idx = int(cur.execute("SELECT value FROM config WHERE key='s_next_index'").fetchone()[0])

    inserted = 0
    for L in LISTINGS:
        if cur.execute("SELECT 1 FROM listings WHERE property_link=?", (L["link"],)).fetchone():
            print(f"skip (exists): {L['link']}")
            continue
        if s_locked:
            s = float(s_locked)
        else:
            s = rotation[idx % len(rotation)]
            idx += 1
        sd = round(math.sqrt(L["ambiguity"] * L["noise"]), 2)
        cur.execute(
            "INSERT INTO listings (date_started, va_id, property_link, location_id, images_n, "
            "s_per_image, ambiguity, noise, quality_sd, quality_verdict, outcome, notes, "
            "price_per_night, rating, reviews_n) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,'In-Progress',?,?,?,?)",
            (DATE, va_id, L["link"], loc_id, L["images_n"], s,
             L["ambiguity"], L["noise"], sd, verdict(sd), L["notes"],
             L["price_per_night"], L["rating"], L["reviews_n"]))
        lid = cur.lastrowid

        # T11 — X-Factor spotted at sourcing
        name, cat, desc = L["x_factor"]
        cur.execute("INSERT OR IGNORE INTO x_factors (name, category, description) VALUES (?,?,?)",
                    (name, cat, desc))
        xf_id = cur.execute("SELECT x_factor_id FROM x_factors WHERE name=?", (name,)).fetchone()[0]
        cur.execute("INSERT OR IGNORE INTO listing_x_factors (listing_id, x_factor_id, spotted_by, note) "
                    "VALUES (?,?,?,?)", (lid, xf_id, "Collin", L["notes"][:120]))

        print(f"listing #{lid}: S={s}  SD={sd} {verdict(sd)}  N={L['images_n']}  {L['link']}")
        inserted += 1

    if not s_locked and inserted:
        cur.execute("UPDATE config SET value=?, updated_at=datetime('now') WHERE key='s_next_index'",
                    (str(idx % len(rotation)),))
        print(f"config.s_next_index -> {idx % len(rotation)}")

    con.commit()
    con.close()
    print(f"done: {inserted} listing(s) written to {DB}")

    # T-all rule: materialize after any write
    subprocess.run([sys.executable if sys.executable else "py",
                    str(TOOLS / "xmotion_materialize.py")], check=False)

if __name__ == "__main__":
    main()
