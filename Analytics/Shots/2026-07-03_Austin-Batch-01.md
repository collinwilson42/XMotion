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

## Batch 1 — six parallel clips (FINAL — locked after full-set CS scout, 7 sheets / 55 frames)

| Clip | Frame | Room / Shot | Preset | Prompt | Result | Notes |
|---|---|---|---|---|---|---|
| 1 | 042.png | Approach — stone path to house | Dolly In | slow dolly forward along the stone path toward the house, eye-level, smooth steady motion, soft dappled daylight, photorealistic, stable geometry, no warping, no morphing | pending | Montage opener; forward-to-house direction |
| 2 | 005.png | Living → dining sight line | FPV Drone | slow FPV glide forward through the living room toward the dining area, continuous flowing motion, eye-level, bright natural light, photorealistic, stable geometry, no warping, no morphing | pending | Watch TV screen shimmer (edge of frame) |
| 3 | 034.png | Kitchen | 360 Orbit | gentle orbit past the counter and cabinetry, bright even lighting, premium finish, steady cinematic motion, photorealistic, stable geometry, no warping, no morphing | pending | Kitchen-dominant frame; 016 is alternate |
| 4 | 010.png | King bedroom (baseline) | Dolly In | slow dolly-in toward the made bed, eye-level, smooth steady gimbal, soft window light, calm steady motion, photorealistic, stable geometry, no warping, no morphing | pending | Cleanest interior — template baseline |
| 5 | 048.png | Hot tub — water beat | Handheld (slow pan) | slow pan across the hot tub water toward the patio dining beyond, gentle steady motion, soft daylight, photorealistic, stable geometry, no warping, no morphing | pending | Water micro-motion sells realism |
| 6 | 053.png | Dusk closer — lit house + steps | Dolly In | slow dolly forward toward the stone steps and the glowing lit house, eye-level, smooth steady motion, warm evening light, photorealistic, stable geometry, no warping, no morphing | pending | Best frame in gallery; string lights = thin-line watch |

**Montage map:** 042 → 005 → 034 → 010 → 048 → 053. Forward momentum on every cut
(approach → through the door → into the home → out to the amenity); light arcs
day → dusk ("arrive in daylight, stay into the evening").

**Full-set scout findings (2026-07-03, CS sheets):** no flamingo-free pool frame
exists — pool beat dropped, hot tub is the water beat. Two light regimes (day +
dedicated twilight set 012/013/051/053/054) — twilight shoot = invested-host
signal, X-Factor candidate. Five sleeping spaces (king, slat-wall queen, iron-bed,
twin-queen boho, bunk room) — market as group/family property. Arch mirror in
011/030/031/035 (avoided); glossy closets 020 (avoided); Universal TV splash in
multiple living frames.

**Batch cost estimate:** ~36 credits (6 clips × ~6 credits, Kling 3.0).

## Bench (batch 2 candidates)

001/044/047 (deck day + golden hour) · 030 (mirror probe — deferred experiment) ·
016 (dining→kitchen w/ slider) · 013/051 (dusk hot tub, purple LED) · 054 (dusk
yard+hammock) · 036 (bunk room, group-capacity beat) · baths 021/025/027.

## Review checklist (fills Ⲱ on render)

Per clip: straight lines stay straight · no melt on doorframes/counter edges ·
reflections stable (030 mirror, 005 TV) · motion reads filmed, not generated ·
float/water motion natural. Judged against the MV rubric → `output_quality` (Ⲱ),
`shot_resonance` (Ѡ = Ⲱ × ⲱ) at T5.

---
*Recorded — WIZX. T3 stamps (model, MQ/SQ percentiles, ⲱ, shot1_prompt) fire on generation; results and Ⲱ fill on review.*
