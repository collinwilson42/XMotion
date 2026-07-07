---
title: XMotion — Automated Tracking
type: ai-skill
domain: analytics-automation
status: active
version: 1.1
updated: 2026-07-04
tags: [xmotion, tracking, automation, reflexes, db, materializer, scoring]
maintainer: XMotion Studio
name: XMotion Automated Tracking
description: X's complete tracking reflex map — every lifecycle moment in the XMotion pipeline and the exact DB write it triggers, unprompted. Use whenever a listing starts, a shot fires, a quality or output score is produced, an offer moves, a video format or overlay template is chosen, or a listing is abandoned. Trigger on log, record, track, insert, update, score, offer, shot, abandoned, dashboard, materialize, rollup, or any mention of XMotion.db. Consolidates DB-Schema section 5, the ⲱ/Ⲱ/Ѡ scoring layer, and format/overlay/border tracking into one contract, with the standing rule that xmotion_materialize.py runs after every write.
tools: filesystem, windows-mcp
db_path: C:\dev\XMotion\Analysis\XMotion.db
signed: wiz-6 (Head of Strategy)
growth:
  - Wire the offer-rollup reflex to also emit a continuity node when a lock triggers
  - Auto-compute Ⲱ from a rendered-video review checklist rather than one holistic judgement
  - Nightly export view -> Master_Tracking_Log.csv mirror for VA-facing visibility
  - Fold EST gate thresholds in once WBS 4.3 assigns model MV
---

# XMotion — Automated Tracking (X's Reflex Map)

> **The contract:** these writes are reflexes, not requests. When a lifecycle
> moment happens in conversation or in reviewed material, X performs the DB
> operation immediately and unprompted, then refreshes the dashboards. One rule
> above all: **after every write, run `py C:\dev\XMotion\_Tools\xmotion_materialize.py`.**

---

## 1. The full trigger table

| #       | Lifecycle moment                                      | DB operation                                                | Fields                                                                                                                                               |
| ------- | ----------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1      | VA starts a listing                                   | `INSERT INTO listings`                                      | `date_started, va_id, property_link, location_id, images_n, s_per_image` (S from rotation, §3), `outcome='In-Progress'`                              |
| T2      | Capture block scouted / quality scored                | `UPDATE listings`                                           | `ambiguity` (1/2/4/8/16), `noise` (1–5), `quality_sd=√(amb×noise)`, `quality_verdict` (PASS ≤2.0 / MAYBE ≤3.5 / FAIL)                                |
| T3      | Shot 1 fired                                          | `UPDATE listings`                                           | `shot1_result` (S/F), `shots_used=1`, **plus scoring stamp**: `model`, `model_quality_pctile`, `shot_quantity_pctile`, `shot_potential=√(MQ×SQ)` (ⲱ) |
| T4      | Shot 2 fired (Two-Shot Rule)                          | `UPDATE listings`                                           | `shot2_result`, `shots_used=2` (re-stamp ⲱ fields if the model changed)                                                                              |
| T5      | Rendered video reviewed                               | `UPDATE listings`                                           | `output_quality` (Ⲱ, 1–100), `shot_resonance = output_quality × shot_potential` (Ѡ)                                                                  |
| T6      | Video format finalized                                | `UPDATE listings`                                           | `frame_aspect` (16:9/9:16/1:1), `content_aspect` (e.g. 3:4), `resolution_out`, `border_type` (none/black/white)                                      |
| T7      | Overlay applied                                       | `UPDATE listings SET overlay_template_id=?`                 | FK into `overlay_templates` (A-series); create the template row first if it's a new A-{x}                                                            |
| T8      | Offer sent                                            | `UPDATE listings SET outcome='Sent'` + `INSERT INTO offers` | `offer_date, offer_price` (295/395)                                                                                                                  |
| T9      | Offer result lands                                    | `UPDATE offers`                                             | `offer_result` (Accepted/Declined/No-Reply), `responded_date`                                                                                        |
| T10     | Listing abandoned                                     | `UPDATE listings`                                           | `outcome='Abandoned'`, `abandon_reason` (Low-Res/Fisheye/Odd-Angles/Too-Few/Lighting/Clutter/Ambiguity)                                              |
| T11     | New X-Factor spotted                                  | `INSERT INTO x_factors` + `INSERT INTO listing_x_factors`   | name, category, spotted_by                                                                                                                           |
| T12     | Every 10 offers                                       | Report `v_s_performance` rollup in chat                     | (config: `rollup_every_offers`)                                                                                                                      |
| T13     | After 20 offers, clear S winner                       | `UPDATE config SET value=? WHERE key='s_locked'`            | (config: `lock_threshold_offers`)                                                                                                                    |
| T14     | Shot declared viable, mp4 saved to `Analytics\Shots\` | `INSERT INTO shots`                                         | `listing_id, va_id, date_produced, tier, job_ids, credits_used (🔗 incl. regens), file_path, status='viable'`                                        |
| T15     | All editing done → AI quality review                  | `UPDATE shots`                                              | `quality_ai` (֎🇦🇮, 1–99 percentile vs. all prior produced shots)                                                                                   |
| T16     | Collin final review                                   | `UPDATE shots`                                              | `quality_final` (֎, 1–99)                                                                                                                            |
| T17     | Preview sent to owner                                 | `UPDATE shots`                                              | `sent_date, status='sent'`                                                                                                                           |
| T18     | Owner response / close                                | `UPDATE shots`                                              | `response_score` (✔️ 1–99, anchored: 1 none · 20 ack · 40 question · 60 interest · 80 verbal yes · 99 closed), `status='responded'/'closed'`         |
| **T-B** | **Before ANY generation**                             | Check `v_budget_status` for the producer                    | if remaining < tier cost → stop, escalate to Collin (reserve decision)                                                                               |
| **T∀**  | **After ANY write above**                             | **`py _Tools\xmotion_materialize.py`**                      | refreshes all 6 dashboards + rematerializes shot filenames from DB truth                                                                             |

## 2. Computed-at-write values (X does the math, SQLite stays portable)

- `quality_sd  = round(sqrt(ambiguity * noise), 2)`
- `shot_potential (ⲱ) = round(sqrt(model_quality_pctile * shot_quantity_pctile), 1)`
- `shot_resonance (Ѡ) = round(output_quality * shot_potential)`
- `efficiency (⚡) = round(sqrt(quality_eff * response_score) / credits_used, 2)` — quality_eff = ֎ final when present, else ֎🇦🇮 AI. Computed by the materializer (portable sqrt); **compare within tier only**.
- Verdict bands: PASS ≤ 2.0 · MAYBE 2.0–3.5 · FAIL > 3.5 (SD gate — see Shot-Quality-Equation skill)
- Labels: ⲱ = Shot Potential (*Before*) · Ⲱ = Shot Yield (*After*) · Ѡ = Shot Resonance (*Balanced*) · ֎🇦🇮/֎ = shot quality AI/final · ✔️ = response · 🔗 = credits-to-viable · ⚡ = efficiency

## 3. S rotation reflex (T1 detail)

Read `config.s_next_index` → assign `s_rotation[index]` → advance index (mod 4) —
**unless** `config.s_locked` is non-empty, then always use the locked S.

## 4. Read map — which view answers which question

| Question                                             | View                               | Dashboard                        |
| ---------------------------------------------------- | ---------------------------------- | -------------------------------- |
| Which pacing (S) sells?                              | `v_s_performance`                  | Images x Seconds                 |
| Which duration bucket sells?                         | `v_duration_performance`           | Images x Seconds                 |
| Which N×S cell sells?                                | `v_grid_cell`                      | Images x Seconds (heatmap)       |
| How is each VA performing (ops + commission)?        | `v_va_scorecard`                   | **Shot Quality Scoring**         |
| Which VA produces the best output? (avg Ⲱ, avg Ѡ)    | `v_va_shot_scoring`                | **Shot Quality Scoring**         |
| Which model earns its credits? (WBS 4.3)             | `v_model_scoring`                  | **Shot Quality Scoring**         |
| Per-shot score ledger (listing layer)                | `v_shot_scoring`                   | Shot Quality Scoring (recent 25) |
| Who produces efficient shots, per tier? (⚡ ablation) | `v_shot_efficiency`                | **Shot Quality Scoring**         |
| What awaits Collin's final ֎ review?                 | `v_shot_efficiency` (review queue) | **Shot Quality Scoring**         |
| Does the pre-gate predict conversion?                | `v_quality_vs_outcome`             | **Shot Quality Scoring**         |
| Capacity + abandonment guardrails                    | `v_monthly_ops`                    | **Shot Quality Scoring**         |
| How much budget remains, per producer?               | `v_budget_status`                  | **Production & Distribution**    |
| Which preview tier gets responses? (A/B)             | `v_tier_ab`                        | **Production & Distribution**    |
| Which market converts?                               | `v_location_performance`           | Locations                        |
| Which frame/content/border combo sells?              | `v_format_combo`                   | Format & Overlay                 |
| Which overlay placement sells?                       | `v_overlay_performance`            | Format & Overlay                 |
| Which X-Factors show up in wins?                     | `v_x_factor_performance`           | X-Factor Relativity              |

> **One metric, one home:** `Shot Quality Scoring` is the single scoring master —
> the full ladder (pre-gate → ⲱ/Ⲱ/Ѡ → ֎/✔️/🔗/⚡). `Production & Distribution` is
> budgets + tier A/B outreach only. The old `Shot Quality` and `Shot Scoring`
> dashboards are retired (2026-07-04) — merged into Shot Quality Scoring.

## 5. Guardrails

- **Single-writer rule:** only Chief's main workstation runs `autosync.py` while
  `XMotion.db` is git-tracked (binaries don't merge). All writes happen there.
- **Never hand-edit dashboards** — they are projections; regenerate instead.
- **Schema changes** go through `_Tools\xmotion_db.py` (idempotent `MIGRATIONS`
  list + `DDL`), never ad-hoc `ALTER` in conversation. Then rerun the builder and
  the materializer, and update `Analysis\XMotion-DB-Schema.md`.
- **Demo lane:** `--demo` on both tools builds/renders `XMotion_demo.db` previews
  without touching production data. Use it to sanity-check any schema change.

*Signed — wiz-6 (Head of Strategy). One skill, complete reflex map. WBS Segment 5 closed.*
