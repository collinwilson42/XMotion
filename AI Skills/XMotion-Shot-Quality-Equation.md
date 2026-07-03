---
title: XMotion — Shot Quality Equation
type: ai-skill
domain: scoring
status: draft
version: 0.6
updated: 2026-07-03
tags: [xmotion, scoring, EST, shot-quality, listing-gate, set-degradation]
maintainer: XMotion Studio
name: XMotion Shot Quality Equation
description: The canonical scoring contract and listing gate. Use when scoring a captured photo set, scouting a capture block off disk, ranking Higgsfield models, scoring a rendered output video, or deciding pass/maybe/fail before any credits are spent. Trigger on score, scout, grade, SD, EST, quality, gate, potential, yield, resonance, the glyphs ⲱ Ⲱ Ѡ, or any capture-block or output review. Defines EST = MV / SD, the glyph layer ⲱ (Shot Potential, Before) / Ⲱ (Shot Yield, After) / Ѡ (Shot Resonance, Balanced), the ambiguity doubling scale (1-16), the linear noise scale (1-5), the SD listing gate verdicts, the post-shot scoring reflex, and the step-by-step scouting protocol over TN_ thumbnails.
tools: filesystem
growth:
  - Lock EST gate thresholds once model MV is assigned (open item, WBS 4.3)
  - Tune noise and ambiguity rubric anchors against more real capture blocks
  - Auto-noise estimation from edge size and JPEG quantization in a later parser pass
  - Amenity tag at capture time so segmentation is recorded, not inferred
  - Decide whether Ѡ gains an SD divisor (Ѡ = Ⲱ·ⲱ/SD) once real scored shots accumulate
  - Consider √(Ⲱ·ⲱ) normalization if the 1-10,000 Ѡ range proves unwieldy in review
---

# XMotion — Shot Quality Equation

> **Status:** v0.5-DRAFT — updated 2026-06-27. Core form LOCKED; EST gate
> thresholds OPEN (calibrate against model MV). Shared-team reference: the
> canonical scoring contract (for the Claude account) and the listing gate
> (for VAs). Keep it professional.

---

## The Glyph Layer (v0.6) — Before / After / Balanced

The MV numerator now carries a glyph and is recorded **per shot**, not only per
model, and a post-render score closes the loop:

| Glyph | Codepoint | Name | Formula | Phase |
|:-----:|-----------|------|---------|-------|
| ⲱ | U+2CB1 | **Shot Potential** | √(Model-Quality %ile × Shot-Quantity %ile), P1–P100 each | *Before* — what the setup puts on the table |
| Ⲱ | U+2CB0 | **Shot Yield** | Output Video Quality, 1–100, judged on the rendered walkthrough | *After* — what the render delivered |
| Ѡ | U+0460 | **Shot Resonance** | Ⲱ × ⲱ (range 1–10,000) | *Balanced* — high only when a strong setup also lands |
| SD | — | Set Degradation | √(Ambiguity × Noise) — unchanged, the input gate divisor | *Gate* |

ⲱ **is** MV — same geometric mean, now stamped onto each listing row at shot time
so per-VA and per-model averages accumulate automatically. EST = ⲱ/SD remains the
pre-spend gate; Ѡ is the *learning* metric that ranks models (WBS 4.3) and VAs on
realized output. Ⲱ is judged by the Claude account against the walkthrough-realism
criteria in the MV rubric below (spatial coherence, camera motion, texture/lighting
fidelity, no hallucinated geometry) — applied to the actual output, not the ceiling.

**Post-shot scoring reflex:** the moment a shot result is recorded, write
`model_quality_pctile`, `shot_quantity_pctile`, `shot_potential` (ⲱ); the moment the
rendered video is reviewed, write `output_quality` (Ⲱ) and `shot_resonance` (Ѡ = Ⲱ·ⲱ),
then run the materializer. Dashboards: `Analysis\Shot Scoring`. Full trigger map:
`AI Skills\XMotion-Automated-Tracking.md`.

> **Scale note (flagged 2026-07-03):** a draft restatement described SD as
> √(Ambiguity(1-10) × Noise(1-10)). The locked contract remains **Ambiguity doubling
> (1/2/4/8/16) × Noise linear (1-5)** — the gate bands below depend on it. If Chief
> intends a scale change, rebase the PASS/MAYBE/FAIL bands in the same edit.

---

## Purpose

One equation, two jobs:

1. **Model selection** — rank the Higgsfield models for the walkthrough use case.
2. **Listing gate** — decide whether a captured photo set is worth a shot, before any credits are spent.

The Claude account is the **judge of picture quality**: it scouts the captured block off disk and scores the denominator. The numerator is a property of the chosen model, assigned once per model.

---

## The Equation

```
EST Shot Quality  =  MV / SD

  MV (Model Value)      = sqrt( Model-Quality %ile  x  Shot-Quality %ile )    1–99 each, higher = better
  SD (Set Degradation)  = sqrt( Ambiguity  x  Noise )                          higher = worse, min 1
```

Both sides are geometric means. The numerator is *goodness percentiles*; the
denominator is *badness multipliers*. A clean set (SD → 1) lets the model score
through at full value; a degraded or ambiguous set divides it down.

**Intentional asymmetry:** Ambiguity runs on a wider **doubling** scale (1–16)
while Noise stays **linear** (1–5). This weights ambiguity heavier on purpose —
it is the dominant failure mode for real-estate photo sets (clean galleries make
noise a minor factor), and the doubling scale survives the square root with real
discrimination at the dangerous end, where a linear scale would collapse.

---

## Numerator — MV (the model, assigned once per model)

- **Model-Quality %ile (1–99):** projected walkthrough-realism ceiling — interior spatial coherence (walls/furniture do not warp), smooth dolly/pan camera motion, texture/lighting fidelity, no hallucinated geometry. Best-case output, not consistency.
- **Shot-Quantity %ile (1–99):** credit efficiency at target settings — how many usable shots the plan budget buys. Cheap fast/turbo variants score high; pro/4k/preview modes score low. Minimum-duration overhead counts against a model when the per-clip target is short.

---

## Denominator — SD (the photos; the Claude account judges per block)

### Ambiguity — doubling scale (1, 2, 4, 8, 16)

Sequencing / interpretive uncertainty for a coherent walkthrough.

| Level | Weight | Meaning |
|-------|:------:|---------|
| Unambiguous | **1** | Clear room-by-room set, single subject (the unit), readable spatial flow |
| Minor | **2** | A couple of redundant angles or one stray shot |
| Moderate | **4** | Mixed clusters needing segmentation (unit vs. amenity), redundant duplicate angles, or unclear room function |
| Heavy | **8** | Many occluded/cluttered/mirror shots, rooms hard to tell apart, conflicting layouts |
| Uninterpretable | **16** | The space cannot be reconstructed; the model will hallucinate |

### Noise — linear scale (1–5)

Signal-level degradation. *(Coarse auto-proxy: manifest LOW-RES flag, edge < 720px.)*

| Score | Meaning                                                                                   |
| :---: | ----------------------------------------------------------------------------------------- |
|   1   | Pristine — 1600px+ shortest edge, sharp, correct exposure/color, no artifacts or overlays |
|   2   | Clean gallery — 720–1600px, sharp, mild downsizing                                        |
|   3   | Soft — visible compression/blur, mild over/under-exposure, or under 720px                 |
|   4   | Degraded — heavy artifacts, motion blur, watermarks/text overlays, fisheye distortion     |
|   5   | Unusable — tiny, severe artifacts, illegible                                              |

---

## Listing Gate (VA-facing) — score SD on the captured block

Pick the Ambiguity weight (1/2/4/8/16) and the Noise score (1–5), compute
`SD = sqrt(Ambiguity × Noise)`:

| SD range | Verdict | Action |
|----------|---------|--------|
| ≤ 2.0 | **PASS** | Shoot as-is. *Optimal zone: SD ≤ 1.4* (unambiguous + clean) |
| 2.0 – 3.5 | **MAYBE** | Viable after prep — segment unit vs. amenity and drop redundant angles, then shoot |
| > 3.5 | **FAIL** | Abandon — log `ABANDONED – IMAGE QUALITY` or `ABANDONED – AMBIGUITY`; do not burn shots |

Reading the bands: minor ambiguity (≤2) can never Fail; moderate ambiguity (4)
passes only with clean photos and otherwise lands in Maybe; heavy/uninterpretable
ambiguity (8/16) Fails the moment any noise is present. The VA controls only SD
(the photos), not MV (the model is fixed per project), so the **listing gate is
the divisor**. The full EST fraction is used for model ranking and borderline
spot-checks.

---

## Scouting Protocol — "scout this folder / scout the most recent block"

When asked to **scout** a capture folder, the Claude account does the following, in order:

1. **Locate the block.** It lives at `Captures\<YYYY-MM-DD>\<BLOCK>\` (e.g. `PM_3-59_4-04`).
2. **Read `_manifest.md`** for the image count, resolutions, and coarse LOW-RES flags.
3. **Read the thumbnails from `TN_<BLOCK>\`** — e.g. `TN_PM_3-59_4-04\001.jpg`. Always read the `TN_` thumbnails, never the full-resolution PNGs: the PNGs exceed the media read size limit, the thumbnails do not. The `TN_` folder is the AI-readable layer the capture parser writes automatically.
4. **Segment the set** into *unit-flow* (the dwelling, room by room) vs. *amenity B-roll* (gym, pool, lobby, exterior); note redundant duplicate angles.
5. **Score** Ambiguity (1/2/4/8/16) and Noise (1–5) from the thumbnails + manifest; compute `SD = sqrt(Ambiguity × Noise)`.
6. **Report**: per-factor scores, SD, the Pass/Maybe/Fail verdict, and the concrete prep actions (which frames to keep for the walkthrough, which to hold as B-roll, which to drop).

The manifest LOW-RES flag is only a hint; the visual judgement from the thumbnails governs the Noise score.

---

## Worked example — block `2026-06-27 / PM_3-59_4-04` (19 images)

- **Noise = 1.7** — all 1440×960-class gallery exports, sharp and clean; only knock is downsizing vs. MLS masters (caps 4K headroom). At the 720 flag threshold, none of this block flags.
- **Ambiguity = 4 (Moderate)** — set mixes one open-plan studio (001/005/010 are the same space from multiple angles) with rooftop amenities (016 gym, 017 pool). Needs segmentation into unit-flow vs. amenity B-roll, plus dedup of redundant studio angles.
- **SD = sqrt(4 × 1.7) ≈ 2.61 → MAYBE.** Segment + dedup, then generate.

*(Sample basis: 6 of 19 viewed. A full-set scout will lock the number.)*

---

## Open / to calibrate

- **EST gate thresholds** — pending model MV assignment (the Higgsfield ranking). Once the top model's MV is fixed, set Pass/Maybe/Fail bands on EST itself, in addition to the SD listing gate above.
- **Rubric anchors** — Noise/Ambiguity tables are draft; tune against more real blocks.
- **Auto-noise** — the manifest edge-flag is a coarse Noise proxy; consider auto-estimating Noise (1–5) from edge + JPEG quantization in a later parser pass.
- **Amenity tag** — consider a capture-time tag (unit / amenity) so segmentation is recorded at copy time rather than inferred later.
