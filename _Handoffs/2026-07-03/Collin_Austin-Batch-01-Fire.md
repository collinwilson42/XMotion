---
title: Handoff — Austin Batch 01, ready to fire
from: WIZX (session 2026-07-03, first live run, Claude Fable 5)
to: next WIZX session (Collin-mode)
date: 2026-07-03
status: batch locked — generation NOT yet fired
---

# State of play

**Done this session:**
1. Memory 10.1 closed — all 10 identity slots saved to account memory.
2. Three Austin listings sourced (Collin), scouted, and scored on the locked scale
   (Amb doubling 1–16 × Noise 1–5, calibrated Noise=1.7 for 1440×960-class):
   - L1 rooms/1522880856219621951 — N=66, SD 1.84 PASS ($337, 4.98★, 48 rev)
   - L2 rooms/630624331006655039 — N=44, SD 1.84 PASS (price/rating/reviews TBD)
   - L3 rooms/1718466620893746332 — N=55, SD 1.30 PASS (NEW listing) ← IN PRODUCTION
3. MV research done: Kling 3.0 = MV leader (~90 = √(MQ 85 × SQ 95), ~6 credits/clip).
   All three listings assigned Kling 3.0. Sora 2 excluded (retiring 9/2026).
4. Batch 1 for L3 locked: 6 clips, 5 with first+last frame pairs + 1 single-frame
   control. Full spec: `Analytics\Shots\2026-07-03_Austin-Batch-01.md` (canonical).
5. XCopy upgraded: 3×3 contact sheets (CS_) auto-build at block close; `--backfill`
   mode added and run. Full-set scout done via CS sheets (7 sheets / 55 frames).
6. X-Factor Relativity Core created + Austin-Batch-01 entry (3 hypotheses linked).
7. DB migrations staged in xmotion_db.py: price_per_night, rating, reviews_n,
   shot1_prompt, shot2_prompt. Schema doc §10 appended.
8. Batch write script staged: `_Tools\xmotion_write_2026-07-03_austin.py`
   (T1+T2+T11 for all 3 listings, S rotation 2.0/2.5/3.0, Collin va-row,
   Austin tier-1 location, materializer auto-run).

**OPEN ITEMS — verify before/at pickup:**
- [ ] CONFIRM Collin ran `py _Tools\xmotion_write_2026-07-03_austin.py` — output
      was never pasted back. If not run, run before anything else (T1/T2 unrecorded).
- [ ] Higgsfield MCP (`npx mcp-remote https://mcp.higgsfield.ai/mcp`) was added
      mid-session and its tools never registered. In the new session: tool_search
      for higgsfield tools FIRST. If present → fire batch natively. If absent →
      check OAuth + per-chat toggle; fallback is Claude-in-Chrome driving the web
      composer (Collin logs in; stage clip 1 visibly before first credit spend).
- [ ] True up SQ percentile with real per-clip credit cost off the generate screen.
- [ ] Confirm account plan tier (affects credit table).
- [ ] Clip 2 pair 005→033: verify 033 facing at full-res; if 180° flip → single 005.
- [ ] Price/rating/reviews backfill for L2 and L3 (fields exist, values pending).
- [ ] D-2 still open: where VAs run capture (blocks VA onboarding).
- [ ] VA onboarding (Jaisa, Richlan) not started — planned after first finished
      walkthrough exists as reference artifact.

**Fire sequence when tools are live:** per Shots doc — Kling 3.0, first+last frame
mode on clips 1/2/3/5/6 (frames win over presets if forced to choose), 5s length,
full-res PNGs from `Captures\2026-07-03\PM_5-30_5-40\`, prompts verbatim incl.
guardrail tails, all six to completion before judging, keep failed renders.
Calibration: 4/6 keepers = good first batch. Then: T3/T5 stamps (model, MQ/SQ,
ⲱ=89.9, shot1_prompt, Ⲱ per clip, Ѡ), paired-vs-control verdict → Findings Log,
EST band calibration begins.

**Session learnings worth keeping:** per-session image read budget ≈ 20 — scout
via CS sheets (9 frames/read) or chat uploads, never frame-by-frame TN reads.
xcopy time-window overlap duplicated one frame across blocks 1/2 (confirmed) —
window removal still on Collin's list; VAs restart xcopy per listing meanwhile.
