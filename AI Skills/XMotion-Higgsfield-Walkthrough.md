---
title: XMotion — Higgsfield Walkthrough Prompting Skill
type: ai-skill
domain: video-generation
status: living
version: 1.0
updated: 2026-06-30
tags: [xmotion, higgsfield, walkthrough, prompting, presets, camera-moves]
maintainer: XMotion Studio
name: XMotion Higgsfield Walkthrough
description: The canonical production craft skill for turning still listing photos into cinematic walkthrough videos in Higgsfield. Use when writing or reviewing a generation prompt, choosing a camera preset for a room, diagnosing warping or drift, or stitching clips into a final walkthrough. Trigger on walkthrough, Higgsfield, preset, camera move, prompt, clip, stitch, or any video generation step. Covers the two rules (no people, slow camera), the preset-to-room map, prompt templates with guardrails, clip length spec, and the per-listing production loop.
tools: filesystem
growth:
  - Findings log: dated entries per model test, preset that warps, prompt fix that held
  - Preset performance ranking once model MV is assigned (first production session)
  - Per-room prompt template refinements from real render results
---

# XMotion — Higgsfield Walkthrough Prompting Skill

> **Purpose:** The canonical production reference for turning still listing photos into cinematic property walkthrough videos in Higgsfield. This is the Studio account's "how we generate" bible and the "what good looks like" production standard. Everything here is field-tested and logged — when we learn something new, it gets added.

---

## The one principle that makes this work

Real estate is one of the **best** possible use cases for AI video — not a stretch. Almost every weakness of AI video comes from two things: **people and fast motion** (warped faces, rubbery limbs, broken physics). A listing clip has neither. It is a slow camera glide over a still, empty room — exactly what these models handle cleanly.

So the entire craft reduces to **two rules**:

1. **Keep people out of the shot.**
2. **Keep the camera move slow and simple.**

Do that, and the output looks *filmed*, not generated.

---

## The biggest quality lever is the PHOTO, not the prompt

Higgsfield animates whatever is in the image. A cluttered, dated, or dark photo becomes a beautifully animated cluttered, dated, dark room. Motion cannot fix a bad space.

This is why the **Shot Quality Equation gate runs first** (see `XMotion-Shot-Quality-Equation.md`). Only frames that pass — clean, bright, well-composed, low Set Degradation — go into production. Garbage in, animated garbage out.

**Never** let Higgsfield invent a room from scratch (its Nano Banana engine can, but for a real listing we sell the *actual* property, not a hallucination).

---

## Preset → Room map

Higgsfield has 250+ camera presets. These are the ones that work for property. **One preset per clip.**

| Preset | Where to use it |
|---|---|
| **Dolly In** | Push forward through an entry or into a room — the strongest opener |
| **360 Orbit** | Circle a kitchen island, dining table, or living-room centerpiece |
| **Dolly Out** | Pull back to reveal the full size of an open space |
| **FPV Drone** | Sweep continuously through an open floor plan (best walkthrough feel) |
| **Handheld** | Natural "walking through it" motion for a room tour |
| **Tilt Up** | Show height — tall windows, vaulted ceilings, double-height space |
| **Crane Up** | Rise over an exterior or a grand interior volume |
| **Boom Down** | Descend a staircase to connect two floors |
| **Static Hero** | Hold on the best room — the thumbnail / money shot |

---

## Prompt templates (camera-first)

Describe the **camera move**, not the scene — the photo already *is* the scene. Keep every move slow. Copy, then swap the room detail.

- **Entry:** `slow dolly forward through the doorway into the room, eye-level, smooth steady gimbal, warm natural daylight, photorealistic, stable geometry, no warping`
- **Open studio / open plan:** `slow FPV glide through the open living space, continuous flowing motion, bright natural light, photorealistic, no warping, no morphing`
- **Kitchen:** `gentle orbit past the counter and cabinetry, bright even lighting, premium finish, steady cinematic motion, photorealistic`
- **Living room:** `slow dolly-out revealing the full living area, soft daylight, steady cinematic pull-back, photorealistic, stable geometry`
- **Bedroom:** `slow dolly-in toward the made bed, soft window light, calm steady motion, photorealistic, no warping`
- **Bathroom:** `slow pan across the vanity and tub, soft diffused light, elegant and steady, photorealistic`
- **Exterior:** `crane up over the front of the property at golden hour, reveal the facade, smooth rising motion, cinematic, photorealistic`

Every prompt ends with the same guardrails: **photorealistic, stable geometry, no warping, no morphing.** These fight the model's tendency to melt straight lines on a move.

---

## Preview Tier Catalog (outreach A/B test — 2026-07 campaign)

Previews are what we SEND to owners; full walkthroughs are produced only after a
deal. Every preview is one tier, assigned by even rotation. All clips Kling 3.0
**pro**, silent, 16:9 (7.5/10s → 17.5 cr, 5s → 8.75 cr at current plan).

| Tier | Length | Composition | Credits | Anchor frames |
|---|---|---|---|---|
| **Tier-1A** | 15s | 10s pro → 5s pro | 26.25 | 4 (2 pairs) |
| **Tier-1B** | 15s | 5s pro → 10s pro | 26.25 | 4 (2 pairs) |
| **Tier-1C** | 15s | 5s → 5s → 5s pro | 26.25 | 4 (chained: A→B, B→C, C→D) |
| **Tier-2A** | 10s | single 10s pro | 17.5 | 2 |
| **Tier-2B** | 10s | two 5s pro | 17.5 | 3–4 |
| **Tier-3A** | 5s | single 5s pro | 8.75 | 2 |

The Tier-1 family holds length (15s) and cost (26.25) constant while varying only
**structure** — long-lead (1A), long-close (1B), or three beats (1C): the clean
ablation. Chained tiers stitch at shared exact frames (pixel-anchored cuts); trim
~0.3s each side of every junction in the edit. Kling takes exactly TWO anchors
per generation (start_image + end_image) at any duration — three enforced frames
is always two generations, never one. Catalog + budgets + response scoring:
`Onboarding\Week 2 - Production & Distribution.md`.

---

## The rules (non-negotiable)

- **Slow moves only.** Speed is what exposes AI artifacts. When in doubt, slower.
- **One move per clip.** Never combine orbit + zoom in a single generation — generate them separately and stitch. Combined moves are where distortion creeps in.
- **No people.** Empty rooms only.
- **Watch mirrors and large windows.** AI warps reflections; frame to minimize big mirrors, or accept a subtle move that hides the drift.
- **Cleanest photo in.** Passes the Shot Quality gate first — always.
- **4–8 seconds per clip.** Longer generations drift and distort. Generate short, trim in the edit.

---

## Clip length + stitch spec

- **Generate** each clip at the model's comfort length (~5s).
- **Trim** in the edit — per-image pacing is an *editing* decision, not a generation one. A 5s generation can become a 2–3s beat in the final cut.
- **Stitch** into a **15–30 second** walkthrough for social, up to ~60s for a listing page.
- **Best room first.** The opener decides whether anyone watches the rest.
- **One slow, well-chosen move per room beats a dozen flashy ones.** Flashy reads as a slideshow; slow-and-continuous reads as a walkthrough. The walkthrough is what we sell.

---

## Studio / open-plan note (important)

For a **studio or open-plan** unit, a single **FPV Drone** or **Handheld** glide can traverse the *entire* living space in one continuous clip — this is the closest AI gets to a real, unbroken walk-through, and it is the best-case product. Lead with it.

**Honest ceiling:** Higgsfield produces per-room glides stitched to *feel* continuous — not one unbroken path through a whole multi-room home. For a house, that is a stitch job. For a studio, one sweep covers most of it. We never claim a true single-take walk we can't deliver.

---

## The production loop (per listing)

1. **Scout** the capture block → Shot Quality Equation → keep only passing frames.
2. **Order** the keepers into a walkthrough flow: enter → living → kitchen → sleeping → bath.
3. Per keeper: **upload** the full-res photo → **pick one preset** → **paste the room prompt** → optionally set start/end frame → **generate** (~2 min).
4. **Review**: any warping, melting, or motion that reveals AI → regenerate slower or pick a gentler preset.
5. **Stitch** best-room-first into 15–30s, add the XMotion overlay, deliver.

---

## Findings log

*Add dated entries as we learn what actually works — model comparisons, presets that warp, prompt tweaks that fixed drift. This section is the compounding asset: every session benefits from every lesson.*

- *(2026-06-30) Skill created from field research + first-principles. First live model test pending on block `PM_3-59_4-04` (studio, FPV sweep on the whole-room reveal frame).*

---

*Maintained by the XMotion Studio. Signed — wiz-4.*
