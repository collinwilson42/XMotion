"""
xmotion_materialize.py - Projects XMotion.db analytics views into color-graded
markdown dashboards for Obsidian. Green -> yellow -> red gradients via inline
HTML spans (rendered in Obsidian reading view).

Run:  py xmotion_materialize.py           -> real DB -> 6 dashboards
      py xmotion_materialize.py --demo    -> demo DB -> '(Demo Preview)' dashboards

X runs this after any write trigger (see trigger table) so dashboards stay live.
"""
import sqlite3, sys, math, os, re
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\dev\XMotion\Analysis")
SHOTS_DIR = Path(r"C:\dev\XMotion\Analytics\Shots")
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

def efficiency(quality_eff, response, credits):
    """LIGHTNING = sqrt(Q_eff x CHECK) / LINK. Computed in Python (portable sqrt)."""
    if not quality_eff or not response or not credits:
        return None
    return round(math.sqrt(quality_eff * response) / credits, 2)


def shot_filename(date, initials, tier, q_ai, q_final, response, credits, eff, glyphs=True):
    """Canonical shot filename, materialized from DB truth.
    Glyph mode:  {date}-{ini}-{tier}-֎🇦🇮{q} | ֎{q}-✔️{r}-🔗{c}-⚡{e}.mp4
    ASCII mode:  {date}-{ini}-{tier}-QA{q} | QF{q}-V{r}-C{c}-E{e}.mp4
    Missing values render as 'na'."""
    def fv(x):
        return "na" if x is None else (f"{x:g}" if isinstance(x, float) else str(x))
    if q_final is not None:
        qtok = ("\u058e" if glyphs else "QF") + fv(q_final)
    else:
        qtok = (("\u058e\U0001F1E6\U0001F1EE" if glyphs else "QA")) + fv(q_ai)
    if glyphs:
        return f"{date}-{initials}-{tier}-{qtok}-\u2714\uFE0F{fv(response)}-\U0001F517{fv(credits)}-\u26A1{fv(eff)}.mp4"
    return f"{date}-{initials}-{tier}-{qtok}-V{fv(response)}-C{fv(credits)}-E{fv(eff)}.mp4"


def sync_shot_filenames(cur):
    """Rename mp4s in Analytics\\Shots to match DB truth; update shots.file_path.
    Runs on every materialization — filenames are a projection, the DB is the source."""
    glyphs = True
    row = cur.execute("SELECT value FROM config WHERE key='filename_glyphs'").fetchone()
    if row and str(row[0]).lower() in ("off", "0", "false", "ascii"):
        glyphs = False
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = cur.execute(
        "SELECT shot_id, date_produced, initials, tier, quality_ai, quality_final,"
        " response_score, credits_used, file_path FROM v_shot_efficiency"
        " WHERE file_path IS NOT NULL").fetchall()
    renamed = 0
    for sid, date, ini, tier, q_ai, q_final, resp, cred, fpath in rows:
        eff = efficiency(q_final if q_final is not None else q_ai, resp, cred)
        target = shot_filename(date, ini or "XX", tier, q_ai, q_final, resp, cred, eff, glyphs)
        cur_path = Path(fpath)
        if not cur_path.is_absolute():
            cur_path = SHOTS_DIR / cur_path
        new_path = cur_path.parent / target
        if cur_path.name == target:
            continue
        try:
            if cur_path.exists():
                os.rename(cur_path, new_path)
            cur.execute("UPDATE shots SET file_path=? WHERE shot_id=?",
                        (str(new_path), sid))
            renamed += 1
            print(f"renamed shot #{sid} -> {target}")
        except OSError as e:
            print(f"[warn] shot #{sid} rename failed: {e}")
    if renamed:
        print(f"filename sync: {renamed} file(s) rematerialized")


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
               chip(r[4], 10, 40, invert=True, fmt="{:.2f}") if r[4] is not None else None,
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

    # ---- Shot Quality Scoring (merged master: gate -> \u2CB1/\u2CB0/\u0460 -> \u058e/\u2714/\U0001F517/\u26A1) ----
    body = header("Shot Quality Scoring Dashboard",
                  "conversion green at 30%+. \u2CB1 Potential &amp; \u2CB0 Yield green at 85+. "
                  "\u0460 Resonance green at 7000+. \u26A1 efficiency green at 4+. "
                  "SD inverted: low = green.")
    body += ("> **The scoring ladder (one document, every layer):**\n"
             "> 1. **Gate** — SD = \u221a(Ambiguity \u00d7 Noise), both 1–99 \u00b7 PASS \u2264 25 \u00b7 MAYBE \u2264 40 \u00b7 FAIL > 40 — spend nothing on a FAIL.\n"
             "> 2. **Listing layer** — \u2CB1 Potential = \u221a(Model-Quality %ile \u00d7 Shot-Quantity %ile) (*Before*) \u00b7\u00b7 "
             "\u2CB0 Yield = Output Video Quality 1\u2013100 (*After*) \u00b7\u00b7 \u0460 Resonance = \u2CB0 \u00d7 \u2CB1 (*Balanced*).\n"
             "> 3. **Shot layer (Week 2)** — \u058e\U0001F1E6\U0001F1EE AI quality 1\u201399 (pending review) \u00b7 \u058e Collin-final 1\u201399 \u00b7 "
             "\u2714\uFE0F response 1\u201399 (1 = none) \u00b7 \U0001F517 credits-to-viable (incl. regens) \u00b7 "
             "\u26A1 = \u221a(\u058e \u00d7 \u2714\uFE0F) / \U0001F517 (final when present, else AI). \u26A1 compares within tier only.\n\n")
    body += "## 1. Does the gate predict conversion?\n\n"
    cols, rows = q(cur, "SELECT quality_verdict, listings, offers_sent, accepted, conversion_rate"
                        " FROM v_quality_vs_outcome ORDER BY CASE quality_verdict"
                        " WHEN 'PASS' THEN 0 WHEN 'MAYBE' THEN 1 ELSE 2 END")
    styled = [[r[0], r[1], r[2], r[3],
               bar(r[4], 0.0, 0.30, fmt="{:.1%}") if r[4] is not None else None] for r in rows]
    body += table(["Verdict", "Listings", "Offers", "Accepted", "Conversion"], styled)
    body += "\n## 2. VA Scorecard (ops + commission)\n\n"
    cols, rows = q(cur, "SELECT name, listings, shots_used, avg_shots, abandon_rate,"
                        " avg_quality_sd, offers_sent, accepted, conversion_rate, commission"
                        " FROM v_va_scorecard")
    styled = [[r[0], r[1], r[2], r[3],
               chip(r[4], 0.0, 0.30, invert=True, fmt="{:.1%}") if r[4] is not None else None,
               chip(r[5], 10, 40, invert=True, fmt="{:.2f}") if r[5] is not None else None,
               r[6], r[7],
               bar(r[8], 0.0, 0.30, fmt="{:.1%}") if r[8] is not None else None,
               f"${r[9]:,.2f}" if r[9] else "-"] for r in rows]
    body += table(["VA", "Listings", "Shots", "Avg Shots", "Abandon", "Avg SD",
                   "Offers", "Accepted", "Conversion", "Commission"], styled)
    body += "\n## 3. VA Scoring Averages (\u2CB1 / \u2CB0 / \u0460)\n\n"
    cols, rows = q(cur, "SELECT name, scored_shots, avg_potential, avg_yield, avg_resonance,"
                        " avg_sd FROM v_va_shot_scoring ORDER BY avg_resonance DESC")
    styled = [[r[0], r[1],
               bar(r[2], 40, 85, fmt="{:.1f}") if r[2] is not None else None,
               bar(r[3], 40, 85, fmt="{:.1f}") if r[3] is not None else None,
               bar(r[4], 1600, 7000, fmt="{:,.0f}") if r[4] is not None else None,
               chip(r[5], 10, 40, invert=True, fmt="{:.2f}") if r[5] is not None else None]
              for r in rows]
    body += table(["VA", "Scored", "Avg \u2CB1 Potential", "Avg \u2CB0 Yield",
                   "Avg \u0460 Resonance", "Avg SD"], styled)
    body += "\n## 4. Model Ranking (feeds MV assignment, WBS 4.3)\n\n"
    cols, rows = q(cur, "SELECT model, scored_shots, avg_potential, avg_yield, avg_resonance"
                        " FROM v_model_scoring ORDER BY avg_resonance DESC")
    styled = [[r[0], r[1],
               chip(r[2], 40, 85, fmt="{:.1f}") if r[2] is not None else None,
               bar(r[3], 40, 85, fmt="{:.1f}") if r[3] is not None else None,
               bar(r[4], 1600, 7000, fmt="{:,.0f}") if r[4] is not None else None]
              for r in rows]
    body += table(["Model", "Scored", "Avg \u2CB1", "Avg \u2CB0", "Avg \u0460"], styled)
    body += "\n## 5. Recent Scored Shots (listing layer)\n\n"
    cols, rows = q(cur, "SELECT date_started, va, model, shot_potential, output_quality,"
                        " shot_resonance, quality_verdict FROM v_shot_scoring"
                        " ORDER BY date_started DESC LIMIT 25")
    styled = [[r[0], r[1], r[2],
               chip(r[3], 40, 85, fmt="{:.1f}") if r[3] is not None else None,
               chip(r[4], 40, 85) if r[4] is not None else None,
               bar(r[5], 1600, 7000, fmt="{:,.0f}") if r[5] is not None else None,
               r[6]] for r in rows]
    body += table(["Date", "VA", "Model", "\u2CB1", "\u2CB0", "\u0460", "Gate"], styled)
    body += "\n## 6. Efficiency by Producer \u00d7 Tier (\u26A1 ablation — within-tier only)\n\n"
    cols, rows = q(cur, "SELECT va, tier, credits_used, response_score, quality_eff,"
                        " review_state, date_produced, status FROM v_shot_efficiency"
                        " ORDER BY va, tier, date_produced")
    agg = {}
    for va, tier, cred, resp, qual, state, date, status in rows:
        e = efficiency(qual, resp, cred)
        if e is not None:
            agg.setdefault((va, tier), []).append(e)
    styled = [[va, tier, len(effs),
               bar(round(sum(effs)/len(effs), 2), 0, 6, fmt="{:.2f}"),
               f"{max(effs):.2f}"]
              for (va, tier), effs in sorted(agg.items())]
    body += table(["Producer", "Tier", "Scored Shots", "Avg \u26A1", "Best \u26A1"], styled)
    body += "\n## 7. Review Queue (\u058e\U0001F1E6\U0001F1EE = awaiting Collin's final \u058e)\n\n"
    cols, rows = q(cur, "SELECT date_produced, va, tier, quality_ai, quality_final,"
                        " response_score, credits_used, review_state, status"
                        " FROM v_shot_efficiency ORDER BY date_produced DESC LIMIT 30")
    styled = [[r[0], r[1], r[2],
               chip(r[3], 1, 99) if r[3] is not None else None,
               chip(r[4], 1, 99) if r[4] is not None else None,
               chip(r[5], 1, 99) if r[5] is not None else None,
               r[6],
               ("\u058e final" if r[7] == "final" else "\u058e\U0001F1E6\U0001F1EE pending"),
               r[8]] for r in rows]
    body += table(["Date", "Producer", "Tier", "\u058e\U0001F1E6\U0001F1EE AI", "\u058e Final",
                   "\u2714\uFE0F", "\U0001F517", "Review", "Status"], styled)
    body += "\n## 8. Monthly Ops (capacity + abandonment guardrails)\n\n"
    cols, rows = q(cur, "SELECT month, listings, shots_used, abandon_rate FROM v_monthly_ops"
                        " ORDER BY month")
    styled = [[r[0], r[1],
               chip(r[2], 0, 100, invert=True) if r[2] is not None else None,
               chip(r[3], 0.0, 0.30, invert=True, fmt="{:.1%}") if r[3] is not None else None]
              for r in rows]
    body += table(["Month", "Listings", "Shots (cap 60-100)", "Abandon Rate (flag >20%)"], styled)
    write("Shot Quality Scoring", "Shot Quality Scoring Dashboard", body)

    # ---- Format & Overlay ----
    body = header("Format & Overlay Dashboard",
                  "conversion green at 30%+. Learns which frame/content/border combo"
                  " and which overlay placement sells.")
    body += "## Frame x Content x Border\n\n"
    cols, rows = q(cur, "SELECT frame_aspect, content_aspect, border_type, listings,"
                        " offers_sent, accepted, conversion_rate FROM v_format_combo"
                        " ORDER BY conversion_rate DESC")
    styled = [[r[0], r[1] or "-", r[2] or "none", r[3], r[4], r[5],
               bar(r[6], 0.0, 0.30, fmt="{:.1%}") if r[6] is not None else None] for r in rows]
    body += table(["Frame", "Content", "Border", "Listings", "Offers", "Accepted",
                   "Conversion"], styled)
    body += "\n## Overlay Template Performance (A-series)\n\n"
    cols, rows = q(cur, "SELECT name, placement, loop_version, listings, offers_sent,"
                        " accepted, conversion_rate FROM v_overlay_performance"
                        " ORDER BY conversion_rate DESC")
    styled = [[r[0], r[1], r[2], r[3], r[4], r[5],
               bar(r[6], 0.0, 0.30, fmt="{:.1%}") if r[6] is not None else None] for r in rows]
    body += table(["Template", "Placement", "Loop", "Listings", "Offers", "Accepted",
                   "Conversion"], styled)
    write("Format & Overlay", "Format & Overlay Dashboard", body)

    # ---- Production & Distribution (Week 2: budget + outreach ONLY; all scoring
    #      lives in Shot Quality Scoring — one metric, one home) ----
    body = header("Production & Distribution Dashboard",
                  "budget remaining inverted: low = red. Response rate green at 50%+.")
    body += ("> **Scope:** credit budgets and the tier A/B outreach experiment. "
             "All quality/efficiency scoring (\u058e, \u2714\uFE0F, \u26A1, review queue) "
             "lives in `Analysis\\Shot Quality Scoring`.\n\n")

    # ---- Credit Pool Budget (preview 66.7% / reserve 33.3%) ----
    def _cfg(k, d):
        r = cur.execute("SELECT value FROM config WHERE key=?", (k,)).fetchone()
        return r[0] if r is not None else d
    plan = float(_cfg("plan_monthly_credits", 1000))
    ppct = float(_cfg("preview_pct", 0.667))
    rpct = float(_cfg("reserve_pct", 0.333))
    prev_pool, res_pool = plan * ppct, plan * rpct
    _m = datetime.now().strftime("%Y-%m")
    prev_spent = cur.execute("SELECT COALESCE(SUM(credits_used),0) FROM shots"
                             " WHERE substr(date_produced,1,7)=? AND COALESCE(status,'')!='reserve'", (_m,)).fetchone()[0]
    res_spent = cur.execute("SELECT COALESCE(SUM(credits_used),0) FROM shots"
                            " WHERE substr(date_produced,1,7)=? AND status='reserve'", (_m,)).fetchone()[0]
    body += "## Credit Pool Budget (this month)\n\n"
    body += (f"> Plan **{plan:g} credits/mo**, split **{ppct:.1%} preview / {rpct:.1%} reserve**. "
             "Previews are what we SEND to owners; reserve funds full walkthroughs for owners who respond.\n\n")
    _pool = [["Preview", f"{ppct:.1%}", f"{prev_pool:g}", f"{prev_spent:g}",
              bar(prev_pool - prev_spent, 0, prev_pool or 1, fmt="{:.0f}")],
             ["Reserve", f"{rpct:.1%}", f"{res_pool:g}", f"{res_spent:g}",
              bar(res_pool - res_spent, 0, res_pool or 1, fmt="{:.0f}")]]
    body += table(["Pool", "Share", "Allocated", "Spent", "Remaining"], _pool)

    body += "\n## Budget Status (month \u00d7 producer, within preview pool)\n\n"
    cols, rows = q(cur, "SELECT month, va, credits_allocated, credits_spent, credits_remaining"
                        " FROM v_budget_status ORDER BY month, credits_allocated DESC")
    styled = [[r[0], r[1], f"{r[2]:g}", f"{r[3]:g}",
               bar(r[4], 0, r[2] or 1, fmt="{:.1f}") if r[4] is not None else None] for r in rows]
    body += table(["Month", "Producer", "Allocated", "Spent", "Remaining"], styled)
    body += ("\n> Budget model (rev 3): monthly credits split **66.7% preview / 33.3% reserve** "
             "(config keys: plan_monthly_credits, preview_pct, reserve_pct). Producer rows draw from the "
             "preview pool. Reserve funds: (1) full walkthroughs for owners who respond to a preview, "
             "(2) a prospective-partner allocation, (3) an efficiency raise for the top \u26A1 producer of the prior month.\n")
    body += "\n## Tier A/B Results (outreach experiment)\n\n"
    cols, rows = q(cur, "SELECT tier, shots, sent, responses, response_rate, avg_response,"
                        " avg_quality, credits FROM v_tier_ab ORDER BY tier")
    styled = [[r[0], r[1], r[2], r[3],
               bar(r[4], 0.0, 0.50, fmt="{:.1%}") if r[4] is not None else None,
               chip(r[5], 1, 99) if r[5] is not None else None,
               chip(r[6], 1, 99) if r[6] is not None else None,
               r[7]] for r in rows]
    body += table(["Tier", "Shots", "Sent", "Responses", "Response Rate",
                   "Avg \u2714\uFE0F", "Avg \u058e", "Credits"], styled)
    body += ("\n> Cross-tier comparison happens HERE on response rate — never on \u26A1 "
             "(the credit denominator structurally favors cheap tiers).\n")
    write("Production & Distribution", "Production & Distribution Dashboard", body)

    # ---- Filename materialization (DB -> Analytics\Shots mp4 names) ----
    if not DEMO:
        sync_shot_filenames(cur)
        con.commit()

    con.close()

if __name__ == "__main__":
    main()
