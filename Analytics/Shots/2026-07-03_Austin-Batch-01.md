---
title: Shots — 2026-07-03 Austin Batch 01
type: shot-record
listing: airbnb.com/rooms/1718466620893746332 (Listing #3, Austin Batch 01)
block: Captures\2026-07-03\PM_5-30_5-40
model: Kling 3.0
mv_provisional: MQ 85 x SQ 95 -> shot_potential (ⲱ) ≈ 89.9
gate: SD 1.30 (Amb 1 x Noise 1.7) — PASS
s_assignment: 3.0 s/image (rotation slot 3)
status: batch 1 staged — 6 parallel clips, results pending
recorded_by: WIZX
date: 2026-07-03
---

# Austin Batch 01 — Shot Record (Listing #3)

**Doctrine for this run:** one move per clip, ~5s generations, slow camera, no people.
The 30–60s walkthrough is an edit product — trim keepers to 2–4s beats, stitch
best-room-first. Regens isolate to the failed clip (~6 credits each).

**Prompt template (confirmed by Collin, 2026-07-03) — goes to `listings.shot1_prompt`:**

```
slow [MOVE] , eye-level, smooth steady motion, [LIGHT], photorealistic, stable geometry, no warping, no morphing
```

Camera-first: describe the move, never the scene — the photo is the scene.
Guardrail suffix is mandatory on every clip.

## Batch 1 — six parallel clips

| Clip | Frame | Room / Shot | Preset | Prompt | Result | Notes |
|---|---|---|---|---|---|---|
| 1 | 010.png | King bedroom (baseline) | Dolly In | slow dolly-in toward the made bed, eye-level, smooth steady gimbal, soft window light, calm steady motion, photorealistic, stable geometry, no warping, no morphing | pending | Cleanest interior — baseline test |
| 2 | 005.png | Living → dining sight line | FPV Drone | slow FPV glide forward through the living room toward the dining area, continuous flowing motion, eye-level, bright natural light, photorealistic, stable geometry, no warping, no morphing | pending | Highest-value clip; probable final-cut opener. Watch TV screen shimmer |
| 3 | TBD (kitchen, ~007–016) | Kitchen | 360 Orbit | gentle orbit past the counter and cabinetry, bright even lighting, premium finish, steady cinematic motion, photorealistic, stable geometry, no warping, no morphing | pending | Frame number: Collin's call (thumbnail reads flaked mid-scout) |
| 4 | 055.png | Flamingo pool → path → house | Dolly In | slow dolly forward along the stone path toward the house, eye-level, smooth steady motion, warm natural light, photorealistic, stable geometry, no warping, no morphing | pending | Personality/establishing shot; New-Listing X-Factor face. Float must drift, not morph |
| 5 | 030.png | Twin-queen boho bedroom | Dolly In | slow dolly-in toward the two beds, eye-level, smooth steady gimbal, soft natural light, calm steady motion, photorealistic, stable geometry, no warping, no morphing | pending | Deliberate mirror probe (arched floor mirror, left edge) — learning clip |
| 6 | 048.png | Hot tub → yard beyond | Handheld (slow pan) | slow pan across the hot tub water toward the garden seating beyond, gentle steady motion, soft dappled daylight, photorealistic, stable geometry, no warping, no morphing | pending | Water surface = legitimate motion subject; ripples sell realism |

**Batch cost estimate:** ~36 credits (6 clips × ~6 credits, Kling 3.0).

## Bench (batch 2 candidates)

006 (living reverse angle, Dolly Out reveal) · 004 (fire-pit circle, Crane Up over
yard/deck/hammock) · 002 (hot tub + facade) · 040 (stock-tank close) · bathroom
coverage — rescout pending.

## Review checklist (fills Ⲱ on render)

Per clip: straight lines stay straight · no melt on doorframes/counter edges ·
reflections stable (030 mirror, 005 TV) · motion reads filmed, not generated ·
float/water motion natural. Judged against the MV rubric → `output_quality` (Ⲱ),
`shot_resonance` (Ѡ = Ⲱ × ⲱ) at T5.

---
*Recorded — WIZX. T3 stamps (model, MQ/SQ percentiles, ⲱ, shot1_prompt) fire on generation; results and Ⲱ fill on review.*
