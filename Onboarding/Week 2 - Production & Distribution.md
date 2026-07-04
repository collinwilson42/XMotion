---
title: Week 2 — Production & Distribution
type: onboarding
audience: Collin + VAs (Jaisa, Richlan) — VA-safe (no full economics)
author: WIZX
date: 2026-07-03
status: active — July 2026 campaign
---

# Week 2 — Production & Distribution

Week 1 taught you to source and score. Week 2 is where XMotion earns: we produce
**preview shots**, send them to property owners, and track what converts. The rule
of the whole system: **sell with the trailer, produce the feature after the deal.**
No full walkthrough is ever built before an owner commits.

## 1. The Preview Tier Catalog (A/B test)

Every outreach gets exactly one preview, assigned by even rotation so tiers get
fair exposure. All clips are Kling 3.0 **pro mode**, silent, 16:9.

| Tier | Length | Composition | Credits |
|---|---|---|---|
| **Tier-1A** | 15s | 10s pro clip → 5s pro clip | 26.25 |
| **Tier-1B** | 15s | 5s pro clip → 10s pro clip | 26.25 |
| **Tier-2A** | 10s | single 10s pro clip | 17.5 |
| **Tier-2B** | 10s | two 5s pro clips | 17.5 |
| **Tier-3A** | 5s | single 5s pro clip | 8.75 |

What the test answers: does *length* drive response (Tier 1 vs 2 vs 3)? Does
*order* matter — long-then-short vs short-then-long (1A vs 1B)? Does *one take*
beat *two beats* at equal length (2A vs 2B)? Distribute evenly, judge nothing
before **5+ sends per tier**.

Content doctrine per current findings: **lead exterior, close dusk** where the
gallery allows. Interiors run pro only. Pairs must share light regime and screen
direction; name any turn in the prompt; demand constant speed through endpoints.

## 2. Credit Budgets (July 2026)

Credits are the unit of trust. Producers hold budgets, not shot counts.

| Producer | Share | July Credits |
|---|---|---|
| Collin | 40% | 459.0 |
| Jaisa | 20% | 229.5 |
| Richlan | 20% | 229.5 |
| House reserve | 20% | 229.5 — three sanctioned uses: (1) finishing production on previews that draw owner interest, (2) onboarding a potential new partner, (3) a performance raise to the prior month's highest-⚡ producer |

Budgets live in `budget_allocations`; spend accrues from `shots.credits_used`;
the Production & Distribution Dashboard shows remaining in real time. A regen
comes out of *your* budget — that's the incentive to gate hard before firing.

**Non-negotiable condition on VA budgets:** every VA credit is spent on a live
call with Collin — see §3. The budget is generous *because* the guidance is
mandatory.

**Growth ladder:** first sale this month → account upgrades to Ultra (3,200
credits/mo) → VA allocations rise to **25% each**, then grow as ⚡ numbers prove
out. Your budget is earned by your efficiency score, not by tenure.

## 3. Group Session Protocol (VA production)

For the first month all VA generation happens in **live group sessions** — no solo firing in month one. The preferred format: **all three on one call** (Collin + Jaisa + Richlan),
the producer taking the shot **screen-shares**, and everyone works the **same
image archive** (the CS contact sheets for the listing in play) to collectively decide on the money shots before a credit moves. Money-shot identification is a
taught skill — the argument IS the training. Purpose: coaching in the moment,
and no mistake gets made twice (check the Findings Log *before* every session,
add to it after).

Session flow, every time:
1. **Gate** — listing passes SD before any credits move (Week 1 skill).
2. **Frame plan** — the group scouts the same CS sheets on the call; WIZX + all
   three nominate money shots and frame pairs; pairs verified full-res by the
   producer sharing screen.
3. **Preflight** — get_cost before fire; confirm budget headroom on the dashboard.
4. **Fire** — VA drives, Collin coaches, WIZX logs job IDs live.
5. **Review** — keep/regen calls as a group; failure modes named out loud and logged.
6. **Score & record** — WIZX writes the shot row; edited keeper goes to the Shots
   folder; materializer runs.

## 4. The Shot Scoring System

Four numbers tell a shot's whole story:

- **🔗 (Credits-to-Viable)** — total credits spent to reach the keeper, regens
  included. Recorded at production close.
- **֎🇦🇮 (AI Quality, pending)** — after all editing is done, WIZX scores the shot
  1–99 as a percentile against every shot already produced. Bootstrap rule: until
  the pool holds 5 scored shots, WIZX scores on the absolute review rubric
  (geometry, motion, realism, anchor strength), then percentile ranking takes over.
- **֎ (Final Quality)** — Collin reviews and adjusts. Same conceptual field, two
  columns in the DB (`quality_ai`, `quality_final`); every projection uses
  **final when present, else AI** — so the system runs on AI scores immediately
  and self-corrects as Collin reviews. The dashboard's review queue shows ֎🇦🇮
  pending items awaiting his pass.
- **✔️ (Response Interest, 1–99)** — scored per outreach. Proposed anchors
  (confirm/adjust): 1 = no response · 20 = viewed/opened, no reply · 40 = replied,
  neutral · 60 = engaged, asking questions · 80 = negotiating price/scope ·
  99 = closed sale.

**⚡ (Efficiency) = √(֎ × ✔️) / 🔗** — quality times market response, discounted
by what it cost. Computed live in the materializer (final score when reviewed,
AI score until then). **Compare ⚡ within a tier only** — the denominator makes
cross-tier comparison structurally unfair to longer previews, which is exactly
why the dashboard ablates by Producer × Tier.

## 5. Shot Files — naming & metadata

When a shot is deemed viable and edited, save the mp4 to
`C:\dev\XMotion\Analytics\Shots\` with any name — then record it. From that point
the **filename is a projection of the database**: every materializer run renames
files to canonical form:

```
{YYYY-MM-DD}-{Initials}-{Tier}-֎🇦🇮{q}|֎{q}-✔️{r}-🔗{c}-⚡{e}.mp4
e.g. 2026-07-05-RD-Tier-1B-֎🇦🇮72-✔️na-🔗17.5-⚡na.mp4      (just produced)
     2026-07-05-RD-Tier-1B-֎68-✔️80-🔗17.5-⚡4.22.mp4        (reviewed + responded)
```

Scores change → next materialization renames the file. Missing values render
`na`. Config `filename_glyphs=off` switches to an ASCII-safe grammar
(`QA/QF·V·C·E`) if any tool chokes on the glyphs — the 🇦🇮 pair is the likely
troublemaker in some apps; the DB keeps the glyph system regardless.

Phase 2 (planned): embed the scoring record as JSON in the mp4's metadata comment
tag at export (`ffmpeg -c copy -metadata`), making every file self-describing
even if renamed outside the system.

## 6. Editing Pipeline

**Now (Week 2):** CapCut. Standard recipe — trim ~0.3s each side of every clip
junction (kills endpoint ease), stitch in montage order, no transitions between
shared-frame junctions (the cut IS the transition), export 1080p 16:9, no audio
or licensed-track-free audio only.

**Next (Week 3 target):** WIZX-driven ffmpeg pipeline — scripted trim/stitch/
fade/overlay/metadata, VA runs one command per preview; plus a frame-sheet
extractor so WIZX can review any rendered clip as a contact sheet (same trick as
capture scouting, applied to video). CapCut remains for creative polish only.
This is how Claude gets real video-editing access: not a GUI, a script layer.

## 7. Outreach & Response Tracking

1. Preview sent → `status='sent'`, `sent_date` recorded, tier logged.
2. Response scored at **day 3** and finalized at **day 7** (✔️ anchors above);
   `status` moves to `responded` or stays `sent`.
3. Interested owner → negotiation. **No further credits spend until terms are
   settled.** Post-agreement production is a new scope with its own shot rows.
4. Sale closed → offer recorded (T6/T7 triggers), ✔️=99, listing outcome updated.

## 8. New Tracking Triggers (extends the trigger table)

| # | Moment | Write |
|---|---|---|
| T12 | Preview shot viable (post-edit) | INSERT `shots` row: va, tier, job_ids, 🔗, file saved |
| T13 | AI quality review (post-edit, automatic) | UPDATE `quality_ai` |
| T14 | Collin score adjustment | UPDATE `quality_final` |
| T15 | Preview sent | UPDATE `sent_date`, `status='sent'` |
| T16 | Response scored (day 3 / day 7) | UPDATE `response_score`, `status` |
| T∀ | After any of the above | run materializer (dashboards + filename sync) |

## 9. Month One Goal & Proof of Concept Expansion Into Month Two 

**Month 1 goal: ≥1 closed company sale in July.** Supporting numbers: budget
supports ~35–43 previews clean (~29 with heavy regen); at even a 10%
response-to-deal rate the funnel closes. Weekly checkpoints: sends per tier on
pace, response rate by tier readable at 5+ sends, ⚡ leaders identified by
producer, Findings Log growing every session. One genuine risk, stated once:
pro-mode keeper rate is built on a small sample — the first two group sessions
true up the real regen multiplier, and budgets absorb it either way.

**The stakes, stated plainly: July is the proof-of-concept month.** One sale
proves the machine — sourcing → gate → preview → response → close — works end
to end. We pass or we fail. If we fail in month 1, we kill it. We won't fail.

**What one sale unlocks (Month 2 — Proof of Concept Expansion):** the account
upgrades to **Ultra (3,200 credits/mo)** and everyone's limits expand for more
reps:

| Producer | Month 1 (1,147.5 cr) | Month 2 Ultra (3,200 cr)* | Reps (previews/mo) |
|---|---|---|---|
| Collin | 40% · 459.0 | 30% · 960 | ~17 → ~37 |
| Jaisa | 20% · 229.5 | **25% · 800** | ~9 → ~30 |
| Richlan | 20% · 229.5 | **25% · 800** | ~9 → ~30 |
| House reserve | 20% · 229.5 | 20% · 640 | — |

*Month 2 split proposed (VA 25% each per the growth ladder is locked; Collin/
reserve shares adjustable). Reps estimated at the ~26.25-credit blended preview
cost — each VA roughly **triples their monthly reps**, which is the point:
proof of concept buys practice volume, practice volume buys efficiency, and ⚡
numbers from Month 2 set the Month 3 allocations.

## 10. Run Order (Collin, once, to activate)

```
py C:\dev\XMotion\_Tools\xmotion_db.py            (new tables, views, budget seed)
py C:\dev\XMotion\_Tools\xmotion_write_2026-07-03_austin.py   (if not yet run)
py C:\dev\XMotion\_Tools\xmotion_materialize.py   (dashboards incl. new P&D board)
```

Then set real initials for filenames:
`UPDATE vas SET initials='XX' WHERE name='...';` (defaults to first two letters).

---
*Drafted — WIZX, 2026-07-03. Cut anything; the DB layer beneath survives any cut.*
