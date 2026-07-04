---
name: Week 2 - Production & Distribution
type: onboarding
domain: va-training
status: live
version: 2.0
updated: 2026-07-04
audience: XMotion VAs (Jaisa, Richlan) + Collin
maintainer: XMotion
signed: Collin (Chief) + wiz-4
---

# Week 2 — Production & Distribution

Week 1: workstation + sourcing. Week 2: the part that makes money — turn photos
into a preview, get it in front of an owner, log what happens.

By the end of this week you can: score a photo block, read the shot list, render
a tiered preview, brand and stitch it, send the offer, and log the result. One
listing at a time. Speed comes after the process is clean.

---

## Part 1 — The Image Scorer

Every photo block gets scored **before a single credit moves**. The Image Scorer
(a skill ai runs) answers three things: which photos to use, which are **money
shots** (the frames that sell the property), and **what order to move through
them**. You are not picking "good photos" — you are letting the scorer draft the
shot list for the whole video. That is the job.

## Part 2 — Running a scoring pass

1. Capture the listing photos into your block (Week 1 tool). They auto-arrange
   into 3×3 thumbnail grids, numbered 001–009+.
2. Send the grid(s) to X: *"Score this block."* Add special instructions if you
   have them ("prioritize outdoor spaces") — your instruction overrides defaults.

Done. The scorer hands back a shot list.

## Part 3 — Reading the output

Three columns matter:

- **Score** — higher = better walkthrough frame. `— drop` means out. No exceptions.
- **Money** — hero rating. High Money frames open or close the video.
- **Bridge** — a sequence like `035 ➢ 054 ➢ 055`: photos that connect in space.
  **Each bridge = one clip.**

## Part 4 — From bridges to clips

The **Bridge Sequence Map** is your production plan:

```
Clip 1:  035 ➢ 054 ➢ 055     (living ➢ hallway ➢ kitchen)
Clip 2:  012 ➢ 018           (bedroom ➢ ensuite)
Clip 3:  001                 (solo hero — the view)
```

- Feed the frames in that exact order — the camera moves the way the scorer planned.
- 2–4 frames per bridge. More drifts.
- Two-shot rule: first render warps → one retry. Second fails → log the reason,
  move on. No third burn, ever.
- Preview doctrine v1 (Batch 1 finding): **lead exterior/dusk**. Both validated
  keepers were exteriors — daylight approach + dusk closer. Save interiors for
  post-sale production where pro mode carries them.

---

## Part 5 — The Preview Tier System (what we actually send)

We do not send full walkthroughs to cold prospects. We send **previews** — one
or two money shots — and only produce the full video against a committed buyer.
Preview cost is ~2% of balance per prospect; the expensive build only ever
happens after a yes. No speculative full builds.

Five tiers, A/B tested. Distribute your sends **evenly across tiers** — the test
only reads if every tier gets reps.

| Tier | Length | Composition | Credits |
|---|---|---|---|
| **Tier-1A** | 15s | 10s pro → 5s pro | 26.25 |
| **Tier-1B** | 15s | 5s pro → 10s pro | 26.25 |
| **Tier-2A** | 10s | single 10s pro | 17.5 |
| **Tier-2B** | 10s | 2× 5s pro | 17.5 |
| **Tier-3A** | 5s | single 5s pro | 8.75 |

**What each tier is testing:** 1A vs 1B = does the long shot lead or close?
2A vs 2B = one continuous move vs a cut? Tier-3 = the floor — is a single money
shot enough to get a reply?

**How we judge the test:** cross-tier winner = **response rate** (Production &
Distribution dashboard). Producer skill within a tier = **⚡ efficiency** (Shot
Quality Scoring dashboard). Never compare ⚡ across tiers — the credit
denominator makes cheap tiers look artificially good.

---

## Part 6 — Credit Budgets (July 2026)

You no longer have a "number of shots." You have a **credit budget**. Every
generation, including regens, spends from it.

| Producer | Share | Credits | ~Capacity |
|---|---|---|---|
| Collin | 40% | 459.0 | ~17 Tier-1 / ~26 Tier-2 / ~52 Tier-3 |
| Jaisa | 20% | 229.5 | ~8 Tier-1 / ~13 Tier-2 / ~26 Tier-3 |
| Richlan | 20% | 229.5 | ~8 Tier-1 / ~13 Tier-2 / ~26 Tier-3 |
| House reserve | 20% | 229.5 | see below |

*(Basis: 1,147.5 credits at allocation. Live remaining is always the Budget
Status table in `Analysis\Production & Distribution` — check it before you
generate.)*

**Reserve purposes (three, in priority order):**
1. **Buffer** — finishing preview clips that get owner interest.
2. **Partner allocation** — a prospective new partner Collin is considering.
3. **Efficiency raise** — awarded to the producer with the highest ⚡ of the
   prior month. The raise is credits: winners get paid in ammunition, which
   compounds into more commission opportunity.

**The mandatory-call rule (non-negotiable):** all VA production happens in a
**group session** — all three on a call, the producer screen-sharing, everyone
working the same contact-sheet archive to argue out the money shots *before* a
credit moves. That argument is the X-Factor training, live, on real inventory.
Solo VA generation is a budget violation, full stop. This rule relaxes as the
numbers prove themselves.

---

## Part 7 — The Shot Scoring System

Every viable shot carries five marks:

| Glyph | Name | Scale | Who sets it |
|---|---|---|---|
| **֎🇦🇮** | AI quality (pending) | 1–99 percentile | X — after ALL editing, scored against every shot already produced |
| **֎** | Final quality | 1–99 | Collin — adjusts the AI score on review |
| **✔️** | Response interest | 1–99 | Whoever logs the owner's reply |
| **🔗** | Credits to viable | credits | Total spend incl. regens |
| **⚡** | Efficiency | derived | **⚡ = √(֎ × ✔️) / 🔗** |

⚡ uses ֎ when Collin has reviewed, else ֎🇦🇮 — same field, different
materialization, and the review queue in the Shot Quality Scoring dashboard
shows exactly what's awaiting his pass. Why this formula holds: quality alone
rewards perfectionism, response alone rewards spam — multiplying them and
dividing by cost rewards **shots that sell cheaply**, which is the business.
The √ dampens one lucky lead from crowning a producer.

**✔️ anchors (so three people score the same event the same way):**
1 = no response · 20 = read/short acknowledgment · 40 = engaged question ·
60 = active interest / negotiating · 80 = verbal yes · 99 = closed sale.

**Filename grammar (materialized — never hand-typed):** when you or X decide a
shot is viable, save the mp4 to `C:\dev\XMotion\Analytics\Shots\`. The
materializer renames it from DB truth on every run:

```
{YYYY-MM-DD}-{Initials}-{Tier}-֎🇦🇮{q} | ֎{q}-✔️{r}-🔗{c}-⚡{e}.mp4
e.g. 2026-07-04-RI-Tier-1B-֎🇦🇮72-✔️na-🔗17.5-⚡na.mp4
```

The DB is the source; the filename is a projection. Missing values render `na`
and fill in as the shot moves through review → send → response. If any tool
mangles the 🇦🇮 flag emoji, `config.filename_glyphs=off` flips to ASCII
(QA/QF-V-C-E) without touching data.

---

## Part 8 — Editing Pipeline

**Now:** CapCut for trim + stitch + export. Recipe per preview: trim ~0.3s at
each junction, concatenate in tier order, export 1080p 16:9, apply the XMotion
glassmorphic overlay (distributed XM marks — studio look, theft protection).

**Week 3 target:** move the mechanical edit to Claude-driven ffmpeg via the
**mcp-video** MCP server (free, open-source, 119 structured tools, preflight
validation). Once connected, X trims/stitches/exports in-session: render comes
back from Higgsfield → X edits → file lands in `Analytics\Shots\` → shot row
writes → materializer names it. Zero marginal cost; CapCut demotes to creative
polish. Install: `pip install mcp-video` + `choco install ffmpeg`. One caution,
stated once: community MCP servers execute code on the machine — Collin vets
the repo before install.

---

## Part 9 — Tracking Triggers (shot layer, T14–T18)

The listing-layer triggers (T1–T13) live in `AI Skills\XMotion-Automated-Tracking.md`.
Week 2 adds the shot layer — X performs these unprompted:

| # | Moment | DB operation |
|---|---|---|
| **T14** | Shot declared viable, mp4 saved to `Analytics\Shots\` | `INSERT INTO shots` — listing_id, va_id, date_produced, tier, job_ids, **🔗 credits_used**, file_path, status='viable' |
| **T15** | All editing done → AI quality review | `UPDATE shots SET quality_ai` (֎🇦🇮, percentile vs. all prior shots) |
| **T16** | Collin reviews | `UPDATE shots SET quality_final` (֎) |
| **T17** | Preview sent to owner | `UPDATE shots SET sent_date, status='sent'` |
| **T18** | Owner responds / deal closes | `UPDATE shots SET response_score (✔️), status='responded'/'closed'` |
| **T-B** | **Before any generation** | Check `v_budget_status` for the producer — if remaining < tier cost, stop and escalate to Collin (reserve decision) |

After every write: `py C:\dev\XMotion\_Tools\xmotion_materialize.py`. Always.

**Where to read the results:** `Analysis\Shot Quality Scoring` = the full
scoring ladder (gate → ⲱ/Ⲱ/Ѡ → ֎/✔️/🔗/⚡, ablation by Producer × Tier, review
queue). `Analysis\Production & Distribution` = budgets + tier A/B outreach.
One metric, one home.

---

## Part 10 — Distribution: sending the offer

1. Export the final preview at spec.
2. Send with the standard offer ($295–$395 by listing). Short, warm, specific to
   their property — X drafts with you.
3. **Log the send immediately (T17).** An unlogged video didn't happen.
4. When the owner replies — yes, no, or anything — tell X right away (T18).
   The ✔️ score is the fuel for the whole A/B test.

---

## Part 11 — Month 1 Goal & Proof of Concept Expansion (Month 2)

**Month 1 (July) is the proof-of-concept month. Binary: pass or fail.**

**Goal: ≥1 closed company sale.** One sale proves the funnel end-to-end —
sourcing → preview → response → close — and triggers the account upgrade to
**Ultra (3,200 credits/month)**. Fail in month one and we kill it. We won't fail.

**What one sale unlocks — everyone's limits increase:**

| Producer | Month 1 (Pro, 1,147.5) | Month 2 (Ultra, 3,200) | Change |
|---|---|---|---|
| Collin | 459.0 (40%) | 960 (30%) | +109% credits, smaller share — VAs are trained |
| Jaisa | 229.5 (20%) | **800 (25%)** | **+249% credits** |
| Richlan | 229.5 (20%) | **800 (25%)** | **+249% credits** |
| Reserve | 229.5 (20%) | 640 (20%) | +179% |

*(Month 2 split is the default proposal — Collin adjusts on the month-1
numbers. VA shares increase gradually beyond 25% as the numbers keep proving.)*

At Ultra, each VA budget funds ~30 Tier-1 previews a month — real rep volume.
The path from 8 previews/month to 30 runs directly through this month's
discipline: clean logging, group sessions, honest ✔️ scores.

**Supporting math:** current balance funds ~35–43 previews clean (~29 with
heavy regen). At even a 10% response-to-deal rate the funnel closes. Weekly
checkpoints: sends per tier on pace, response rate readable at 5+ sends per
tier, ⚡ leaders identified, Findings Log growing every session. One genuine
risk, stated once: pro-mode keeper rate is built on a small sample — the first
two group sessions true up the real regen multiplier, and the reserve absorbs
it either way.

---

## Part 12 — Your X-Factor this week

The skill that separates a good VA from a great one: **reading a photo block
like the scorer does before you send it.** Guess the money shots and bridges,
then compare against the scorer's output. When your instinct matches the
machine, your sourcing gets faster, your picks get sharper, and your ⚡ climbs —
and ⚡ is what earns the reserve raise.

You're building a real skill, not doing busywork. Ask X anything.

---

## End-of-week checklist
- [ ] Scored at least 5 blocks and read every Bridge Map correctly
- [ ] Produced previews in at least 3 different tiers, inside budget, in group session
- [ ] Every viable shot saved to `Analytics\Shots\` and logged (T14)
- [ ] Applied the branded overlay + stitched per the tier spec
- [ ] Sent at least 3 real offers, each logged at send time (T17)
- [ ] Reported at least one owner reply with an anchored ✔️ score (T18)
