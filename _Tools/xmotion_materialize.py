"""
xmotion_materialize.py - Projects XMotion.db analytics views into color-graded
markdown dashboards for Obsidian. Green -> yellow -> red gradients via inline
HTML spans (rendered in Obsidian reading view).

Run:  py xmotion_materialize.py           -> real DB -> 4 dashboards
      py xmotion_materialize.py --demo    -> demo DB -> '(Demo Preview)' dashboards

X runs this after any write trigger (see trigger table) so dashboards stay live.
"""
import sqlite3, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\dev\XMotion\Analysis")
DEMO = "--demo" in sys.argv
DB = ROOT / ("XMotion_demo.db" if DEMO else "XMotion.db")
SUFFIX = " (Demo Preview)" if DEMO else ""
STAMP = datetime.now().strftime("%Y-%m-%d %H:%M")

GREEN, YELLOW, RED = (34, 197, 94), (234, 179, 8), (239, 68, 68)

def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def grade(value, lo, hi, invert=False):
    """Map value in [lo,hi] to a hex color on the green-yellow-red gradient.
    Default: hi = green. invert=True: lo = green (for badness metrics like SD)."""
    if value is None:
        return "#6b7280"
    t = max(0.0, min(1.0, (value - lo) / (hi - lo) if hi != lo else 0.5))
    if invert:
        t = 1.0 - t
    rgb = lerp(RED, YELLOW, t / 0.5) if t < 0.5 else lerp(YELLOW, GREEN, (t - 0.5) / 0.5)
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def chip(value, lo, hi, invert=False, fmt="{}"):
    if value is None:
        return "<span style='color:#6b7280'>-</span>"
    return f"<span style='color:{grade(value, lo, hi, invert)}'>&#9679;</span> {fmt.format(value)}"

def bar(value, lo, hi, invert=False, width=12, fmt="{}"):
    if value is None:
        return "-"
    t = max(0.0, min(1.0, (value - lo) / (hi - lo) if hi != lo else 0.5))
    n = max(1, round(t * width))
    color = grade(value, lo, hi, invert)
    return f"<span style='color:{color}'>{'&#9608;' * n}</span> **{fmt.format(value)}**"

def q(cur, sql):
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()

def table(cols, rows):
    if not rows:
        return "> *No data yet - this dashboard populates as WIZX records listings.*\n"
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(c) if c is not None else "-" for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"

def header(title, legend):
    return (f"# {title}{SUFFIX}\n\n"
            f"> Materialized from `{DB.name}` at {STAMP} by xmotion_materialize.py. "
            f"Do not hand-edit - regenerate instead.\n>\n> Gradient: {legend}\n\n")

def write(folder, title, content):
    d = ROOT / folder
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{title}{SUFFIX}.md"
    p.write_text(content, encoding="utf-8")
    print(f"wrote {p}")

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # ---- Locations ----
    cols, rows = q(cur, "SELECT city, region, market_tier, listings, avg_quality_sd,"
                        " offers_sent, accepted, conversion_rate, revenue"
                        " FROM v_location_performance ORDER BY conversion_rate DESC")
    body = header("Locations Dashboard",
                  "conversion green at 30%+, red at 0. SD inverted: low SD = green.")
    styled = [[r[0], r[1], r[2], r[3],
               chip(r[4], 1.0, 3.5, invert=True, fmt="{:.2f}") if r[4] is not None else None,
               r[5], r[6],
               bar(r[7], 0.0, 0.30, fmt="{:.1%}") if r[7] is not None else None,
               f"${r[8]:,.0f}" if r[8] else "-"] for r in rows]
    body += table(["City", "Region", "Tier", "Listings", "Avg SD", "Offers",
                   "Accepted", "Conversion", "Revenue"], styled)
    write("Locations", "Locations Dashboard", body)

    # ---- Images x Seconds (the grid heatmap) ----
    body = header("Images x Seconds Dashboard",
                  "cell color = conversion rate (green 30%+). Row/col totals below.")
    cols, rows = q(cur, "SELECT images_n, s_per_image, offers_sent, accepted, conversion_rate"
                        " FROM v_grid_cell")
    cell = {(r[0], r[1]): r for r in rows}
    n_bands = (5, 8, 10, 12, 15, 18, 20, 25)
    s_bands = (2.0, 2.5, 3.0, 4.0)
    heat = ["| N \\ S | " + " | ".join(f"{s}s/im" for s in s_bands) + " |",
            "|---|" + "---|" * len(s_bands)]
    for n in n_bands:
        row = [f"| **{n}**"]
        for s in s_bands:
            r = cell.get((n, s))
            if r and r[2]:
                row.append(chip(r[4], 0.0, 0.30, fmt="{:.0%}") + f" ({r[3]}/{r[2]})")
            else:
                row.append("-")
        heat.append(" | ".join(row) + " |")
    body += "\n".join(heat) + "\n\n## S-Value Performance (per-image pacing)\n\n"
    cols, rows = q(cur, "SELECT s_per_image, listings, offers_sent, accepted, conversion_rate,"
                        " revenue FROM v_s_performance ORDER BY s_per_image")
    styled = [[f"{r[0]}s/im", r[1], r[2], r[3],
               bar(r[4], 0.0, 0.30, fmt="{:.1%}") if r[4] is not None else None,
               f"${r[5]:,.0f}" if r[5] else "-"] for r in rows]
    body += table(["S", "Listings", "Offers", "Accepted", "Conversion", "Revenue"], styled)
    body += "\n## Duration Performance (S*N output side)\n\n"
    cols, rows = q(cur, "SELECT duration_rounded, listings, offers_sent, accepted,"
                        " conversion_rate FROM v_duration_performance ORDER BY duration_rounded")
    styled = [[f"{r[0]}s", r[1], r[2], r[3],
               bar(r[4], 0.0, 0.30, fmt="{:.1%}") if r[4] is not None else None] for r in rows]
    body += table(["Duration", "Listings", "Offers", "Accepted", "Conversion"], styled)
    write("Images x Seconds", "Images x Seconds Dashboard", body)

    # ---- X-Factor Relativity ----
    body = header("X-Factor Relativity Dashboard",
                  "conversion green at 30%+. An X-Factor earns green by showing up in accepted offers.")
    cols, rows = q(cur, "SELECT name, category, listings, offers_sent, accepted, conversion_rate"
                        " FROM v_x_factor_performance ORDER BY conversion_rate DESC, listings DESC")
    styled = [[r[0], r[1] or "-", r[2], r[3], r[4],
               bar(r[5], 0.0, 0.30, fmt="{:.1%}") if r[5] is not None else None] for r in rows]
    body += table(["X-Factor", "Category", "Listings", "Offers", "Accepted", "Conversion"], styled)
    body += ("\n> Log an X-Factor: `INSERT INTO x_factors (name, category, description)` then link via"
             " `listing_x_factors`. WIZX records these on the spot during sourcing review.\n")
    write("X-Factor Relativity", "X-Factor Relativity Dashboard", body)

    # ---- Shot Quality ----
    body = header("Shot Quality Dashboard",
                  "verdict conversion green at 30%+. VA avg SD inverted: low = green.")
    cols, rows = q(cur, "SELECT quality_verdict, listings, offers_sent, accepted, conversion_rate"
                        " FROM v_quality_vs_outcome ORDER BY CASE quality_verdict"
                        " WHEN 'PASS' THEN 0 WHEN 'MAYBE' THEN 1 ELSE 2 END")
    styled = [[r[0], r[1], r[2], r[3],
               bar(r[4], 0.0, 0.30, fmt="{:.1%}") if r[4] is not None else None] for r in rows]
    body += "## Does the gate predict conversion?\n\n"
    body += table(["Verdict", "Listings", "Offers", "Accepted", "Conversion"], styled)
    body += "\n## VA Scorecard\n\n"
    cols, rows = q(cur, "SELECT name, listings, shots_used, avg_shots, abandon_rate,"
                        " avg_quality_sd, offers_sent, accepted, conversion_rate, commission"
                        " FROM v_va_scorecard")
    styled = [[r[0], r[1], r[2], r[3],
               chip(r[4], 0.0, 0.30, invert=True, fmt="{:.1%}") if r[4] is not None else None,
               chip(r[5], 1.0, 3.5, invert=True, fmt="{:.2f}") if r[5] is not None else None,
               r[6], r[7],
               bar(r[8], 0.0, 0.30, fmt="{:.1%}") if r[8] is not None else None,
               f"${r[9]:,.2f}" if r[9] else "-"] for r in rows]
    body += table(["VA", "Listings", "Shots", "Avg Shots", "Abandon", "Avg SD",
                   "Offers", "Accepted", "Conversion", "Commission"], styled)
    body += "\n## Monthly Ops (capacity + abandonment guardrails)\n\n"
    cols, rows = q(cur, "SELECT month, listings, shots_used, abandon_rate FROM v_monthly_ops"
                        " ORDER BY month")
    styled = [[r[0], r[1],
               chip(r[2], 0, 100, invert=True) if r[2] is not None else None,
               chip(r[3], 0.0, 0.30, invert=True, fmt="{:.1%}") if r[3] is not None else None]
              for r in rows]
    body += table(["Month", "Listings", "Shots (cap 60-100)", "Abandon Rate (flag >20%)"], styled)
    write("Shot Quality", "Shot Quality Dashboard", body)

    con.close()

if __name__ == "__main__":
    main()
