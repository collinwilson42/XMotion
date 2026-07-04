---
title: XMotion — Shot Quality Equation
type: ai-skill
domain: scoring
status: live
version: 1.0
updated: 2026-07-04
tags: [xmotion, scoring, shot-quality, listing-gate, set-degradation, image-scorer]
maintainer: XMotion Studio
name: XMotion Shot Quality Equation
description: The canonical scoring contract and listing gate. Use when scoring a captured photo set, scouting a capture block off disk, scoring a rendered output video, or deciding pass/maybe/fail before any credits are spent. Trigger on score, scout, grade, SD, quality, gate, potential, yield, resonance, the glyphs ⲱ Ⲱ Ѡ, or any capture-block or output review. Canonical equation is the Image Scorer v2 form — Score = √(Flow × Quality × Location × MoneyShot) / √(Ambiguity × Noise), all six factors 1–99. Defines the block-level SD gate (SD = √(Ambiguity × Noise), PASS ≤ 25 / MAYBE ≤ 40 / FAIL > 40), the glyph ladder ⲱ (Shot Potential, Before) / Ⲱ (Shot Yield, After) / Ѡ (Shot Resonance, Balanced), the post-shot scoring reflex, and the scouting protocol over TN_ thumbnails. The old EST = MV/SD formula is RETIRED (2026-07-04).
tools: filesystem
growth:
  - Calibrate the 1–99 rubric anchors and gate bands against real capture blocks
  - Calibrate the ⲱ = Catalog/10 normalization once scored shots accumulate
  - Auto-noise estimation from edge size and JPEG quantization in a later parser pass
  - Amenity tag at capture time so segmentation is recorded, not inferred
  - Decide whether Ѡ gains an SD divisor once real scored shots accumulate
---

# XMotion — Shot Quality Equation

> **Status:** v1.0 — 2026-07-04. **EST = MV/SD is retired for good.** The Image
> Scorer v2 equation is the single canonical scoring form; Ambiguity and Noise
> are now 1–99 like every other factor in the system. One scale family,
> everywhere: 1–99 desirability up top, 1–99 uncertainty below, geometric means
> on both sides.

---

## The Canonical Equation (Image Scorer v2 — one form, every level)

```
Score = √( Flow × Quality × Location × MoneyShot )  /  √( Ambiguity × Noise )
```

All six factors are **1–99 integers**. Applied per image by the Image Scorer
(`AI Skills\XMotion-Image-Scorer.md` — the full rubric, bridges, and keep rule
live there). Averaged over a block, the same form yields the **Catalog score**:

```
Catalog = √( avgFlow × avgQual × avgLoc × avgMoney ) / √( avgAmb × avgNoise )
```

The **denominator alone** is the pre-spend gate; the **full ratio** is the
potential measure. Same fraction, two jobs.

## The SD Gate (block level — spend nothing on a FAIL)

```
SD = √( Ambiguity × Noise )        both 1–99, higher = worse
```

| SD range | Verdict   | Action                                                                                  |
| -------- | --------- | --------------------------------------------------------------------------------------- |
| ≤ 25     | **PASS**  | Shoot as-is. *Optimal zone: SD ≤ 15 (unambiguous + clean)*                              |
| 25–40    | **MAYBE** | Viable after prep — segment unit vs. amenity, drop redundant angles, then shoot         |
| > 40     | **FAIL**  | Abandon — log `ABANDONED – IMAGE QUALITY` or `ABANDONED – AMBIGUITY`; do not burn shots |

*(Bands are the old PASS ≤ 2.0 / ≤ 3.5 semantics mapped onto 1–99 — every
historical verdict survives the rescale unchanged. Draft anchors; calibrate
against real blocks.)*

### Ambiguity — 1–99 rubric anchors

Sequencing / interpretive uncertainty for a coherent walkthrough.

| Anchor | Level           | Meaning                                                                                                      |
| :----: | --------------- | ------------------------------------------------------------------------------------------------------------ |
| **10** | Unambiguous     | Clear room-by-room set, single subject (the unit), readable spatial flow                                     |
| **25** | Minor           | A couple of redundant angles or one stray shot                                                               |
| **40** | Moderate        | Mixed clusters needing segmentation (unit vs. amenity), duplicate angles, or unclear room function           |
| **70** | Heavy           | Many occluded/cluttered/mirror shots, rooms hard to tell apart, conflicting layouts                          |
| **95** | Uninterpretable | The space cannot be reconstructed; the model will hallucinate                                                |

### Noise — 1–99 rubric anchors

Signal-level degradation. *(Coarse auto-proxy: manifest LOW-RES flag, edge < 720px.)*

| Anchor | Meaning                                                                                   |
| :----: | ----------------------------------------------------------------------------------------- |
| **10** | Pristine — 1600px+ shortest edge, sharp, correct exposure/color, no artifacts or overlays |
| **25** | Clean gallery — 720–1600px, sharp, mild downsizing                                        |
| **40** | Soft — visible compression/blur, mild over/under-exposure, or under 720px                 |
| **70** | Degraded — heavy artifacts, motion blur, watermarks/text overlays, fisheye distortion     |
| **95** | Unusable — tiny, severe artifacts, illegible                                              |

Reading the bands with the anchors: minor ambiguity (≤ 25) can only FAIL against
badly degraded photos; moderate ambiguity (40) passes only with pristine photos
and otherwise lands MAYBE; heavy ambiguity (70+) fails the moment noise leaves
the pristine zone. Ambiguity remains the dominant failure mode by design — the
anchors are spaced to keep discrimination at the dangerous end.

---

## The Glyph Ladder — Before / After / Balanced

| Glyph | Codepoint | Name               | Formula                                                         | Phase                                                 |
| :---: | --------- | ------------------ | --------------------------------------------------------------- | ----------------------------------------------------- |
|   ⲱ   | U+2CB1    | **Shot Potential** | Catalog / 10, capped at 99                                      | *Before* — what the keeper set puts on the table      |
|   Ⲱ   | U+2CB0    | **Shot Yield**     | Output Video Quality, 1–100, judged on the rendered walkthrough | *After* — what the render delivered                   |
|   Ѡ   | U+0460    | **Shot Resonance** | Ⲱ × ⲱ (range 1–10,000)                                          | *Balanced* — high only when a strong setup also lands |
|  SD   | —         | Set Degradation    | √(Ambiguity × Noise), 1–99                                      | *Pre-Gate*                                            |

**ⲱ is now derived from the canonical equation** — the Catalog score of the
keeper set, normalized to 1–99 (÷10, cap 99; a strong clean block lands in the
80s, a mediocre one in the 20s — draft normalization, calibrate as data lands).
The old ⲱ = √(Model-Quality %ile × Shot-Quantity %ile) is retired with MV; the
`model_quality_pctile` / `shot_quantity_pctile` columns remain in the DB as
legacy (never populated on real data).

**Model ranking (WBS 4.3) is now purely empirical:** models are ranked on
realized Ѡ in `v_model_scoring` — no assigned MV, no pending thresholds. The
D-3 open decision closes with this retirement.

**Week 2 shot layer** — per produced *preview shot* (the `shots` table),
downstream of the listing layer above: ֎🇦🇮 AI quality (1–99 percentile,
post-edit, pending review) → ֎ Collin-final (1–99) · ✔️ response interest
(1–99, 1 = none) · 🔗 credits-to-viable (incl. regens) · **⚡ = √(֎ × ✔️) / 🔗**
(final when present, else AI; within-tier comparison only). Full contract:
`Onboarding\Week 2 - Production & Distribution.md` §7; triggers T14–T18 in
`XMotion-Automated-Tracking.md`.

**Post-shot scoring reflex:** the moment keepers are scored, write the SD
factors and `shot_potential` (ⲱ); the moment the rendered video is reviewed,
write `output_quality` (Ⲱ) and `shot_resonance` (Ѡ = Ⲱ·ⲱ), then run the
materializer. Dashboard: `Analysis\Shot Quality Scoring` (the merged scoring
master). Full trigger map: `AI Skills\XMotion-Automated-Tracking.md`.

---

## Scouting Protocol

When asked to **scout** a capture folder, WIZX does the following, in order:

1. **Locate the block.** `Captures\<YYYY-MM-DD>\<BLOCK>\` (e.g. `PM_3-59_4-04`).
2. **Read `_manifest.md`** for image count, resolutions, and coarse LOW-RES flags.
3. **Read the thumbnails from `TN_<BLOCK>\`** — always the `TN_` thumbnails,
   never the full-resolution PNGs (PNGs exceed the media read limit; thumbnails
   are the AI-readable layer the capture parser writes automatically).
4. **Segment the set** into *unit-flow* (the dwelling, room by room) vs.
   *amenity B-roll* (gym, pool, lobby, exterior); note redundant duplicate angles.
5. **Score** Ambiguity (1–99) and Noise (1–99) from thumbnails + manifest;
   compute `SD = √(Ambiguity × Noise)`. For a full pass, run the Image Scorer
   per frame — the block gate and the per-image scores share the same factors.
6. **Report**: factor scores, SD, Pass/Maybe/Fail verdict, and concrete prep
   actions (keepers for the walkthrough, B-roll holds, drops).

The manifest LOW-RES flag is only a hint; visual judgement from the thumbnails
governs the Noise score.

---

## Worked example — block `2026-06-27 / PM_3-59_4-04` (19 images)

- **Noise = 20** — all 1440×960-class gallery exports, sharp and clean; only
  knock is downsizing vs. MLS masters (caps 4K headroom). Sits between the
  pristine (10) and clean-gallery (25) anchors.
- **Ambiguity = 40 (Moderate)** — one open-plan studio (001/005/010 same space,
  multiple angles) mixed with rooftop amenities (016 gym, 017 pool). Needs
  segmentation into unit-flow vs. amenity B-roll, plus dedup.
- **SD = √(40 × 20) ≈ 28.3 → MAYBE.** Segment + dedup, then generate.

*(Same block, same verdict as under the retired scale — the rescale is
semantics-preserving.)*

---

## Retired — EST = MV/SD (2026-07-04, Collin directive)

The original model-selection equation `EST = MV / SD` with
`MV = √(Model-Quality %ile × Shot-Quantity %ile)` is **retired for good**,
along with its doubling ambiguity scale (1–16), linear noise scale (1–5), and
the never-locked EST gate thresholds. It was superseded before ever scoring
real data: the Image Scorer v2 equation covers the numerator's job with
factors we can actually judge per frame, and model ranking runs on realized Ѡ
instead of an assigned ceiling. Historical rows (3 listings, Austin batch)
were rescaled to 1–99 on retirement with verdicts unchanged.

---

## Open / to calibrate

- **Rubric anchors + gate bands** — 1–99 anchors and PASS ≤ 25 / MAYBE ≤ 40 /
  FAIL > 40 are drafts; tune against more real blocks.
- **ⲱ normalization** — Catalog/10 cap 99 is a draft; recheck once dashboards
  hold 20+ scored shots.
- **Auto-noise** — consider auto-estimating Noise from edge + JPEG quantization
  in a later parser pass.
- **Amenity tag** — capture-time unit/amenity tag so segmentation is recorded,
  not inferred.
