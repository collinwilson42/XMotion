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
Per Image Score = √( Flow × Quality × Location × MoneyShot )  /  √( Ambiguity × Noise )
```

All six factors are **1–99 integers**. Applied per image by the Image Scorer
(`AI Skills\XMotion-Image-Scorer.md` — the full rubric, bridges, and keep rule
live there). Averaged over a block, the same form yields the **Catalog score**:

```
ⲱ = √( avgFlow × avgQual × avgLoc × avgMS ) / √( avgAmb × avgNoise )
```

The **denominator alone** is the pre-spend gate; the **full ratio** is the
potential measure. Same fraction, two jobs.

## The **⊜** Gate (block level — spend nothing on a FAIL)

```
⊜ = √( Ambiguity × Noise )        both 1–99, higher = worse
```

| **⊜** range | Verdict   | Action                                                                                  |
| ----------- | --------- | --------------------------------------------------------------------------------------- |
| ≤ 20        | **PASS**  | Shoot as-is. *Optimal zone: **⊜** ≤ 15 (unambiguous + clean)*                           |
| 20–30       | **MAYBE** | Viable after prep — segment unit vs. amenity, drop redundant angles, then shoot         |
| > 30        | **FAIL**  | Abandon — log `ABANDONED – IMAGE QUALITY` or `ABANDONED – AMBIGUITY`; do not burn shots |

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

| Glyph | Codepoint | Name                | Formula                                                          | Phase                                            |
| :---: | --------- | ------------------- | ---------------------------------------------------------------- | ------------------------------------------------ |
|   ⊜   | U+229C    | **Set Degradation** | √(Avg_Ambiguity × Avg_Noise), 1–99                               | **Pre-Shot Gate**                                |
|   ⲱ   | U+2CB1    | **Shot Potential**  | √( avgFlow × avgQual × avgLoc × avgMS ) / √( avgAmb × avgNoise ) | *Before* — what the keeper set puts on the table |
|   Ⲱ   | U+2CB0    | **Shot Yield**      | √(֎🇦🇮 × ✔️) / 🔗                                               | *After* — what the render delivered              |
|   Ѡ   | U+0460    | **Shot Resonance**  | Ⲱ × ⲱ / 2                                                        | *Balanced* — when a strong setup also lands      |


**Post Shot Layer** — per produced *preview shot* (the `shots` table),
downstream of the listing layer above: ֎🇦🇮 AI quality (1–99 percentile,
post-edit, pending review) → ֎ Collin-final (1–99) · ✔️ response interest
(1–99, 1 = none) · 🔗 credits-to-viable (incl. regens) · **Ⲱ = √(֎ × ✔️) / 🔗**
(final when present, else AI; within-tier comparison only). Full contract:
`Onboarding\Week 2 - Production & Distribution.md` §7; triggers T14–T18 in
`XMotion-Automated-Tracking.md`.

**Post-shot scoring reflex:** the moment keepers are scored, write the ⊜
factors and `shot_potential` (ⲱ); the moment the rendered video is reviewed,
write `output_quality` (Ⲱ) and `shot_resonance` (Ѡ = Ⲱ · ⲱ / 2), then run the
materializer. Dashboard: `Analysis\Shot Quality Scoring` (the merged scoring
master). Full trigger map: `AI Skills\XMotion-Automated-Tracking.md`.


---

*XMotion Studio. Signed — Collin.*
