---
title: Shots — 2026-07-03 Austin Batch 01
type: shot-record
listing: airbnb.com/rooms/1718466620893746332 (Listing #3, Austin Batch 01)
block: Captures\2026-07-03\PM_5-30_5-40
model: Kling 3.0
mv_provisional: MQ 85 x SQ 95 -> shot_potential (ⲱ) ≈ 89.9
gate: SD 1.30 (Amb 1 x Noise 1.7) — PASS
s_assignment: 3.0 s/image (rotation slot 3)
status: batch 1 FIRED 2026-07-03 — 6 jobs generating (Kling 3.0, std, 5s, silent, ~45 credits)
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

| Clip | Frames (start → end) | Room / Shot | Preset | Prompt | Result | Notes |
|---|---|---|---|---|---|---|
| 1 | 045.png → 042.png | Approach — yard path to house | Dolly In | slow dolly forward along the stone path toward the house, eye-level, smooth steady motion, soft dappled daylight, photorealistic, stable geometry, no warping, no morphing | pending | Paired; both daylight, forward-to-house |
| 2 | 005.png → 033.png ⚠ | Living → dining sight line | FPV Drone | slow FPV glide forward through the living room toward the dining area, continuous flowing motion, eye-level, bright natural light, photorealistic, stable geometry, no warping, no morphing | pending | VERIFY 033 facing at full-res — if 180 flip, revert to single 005. Watch TV shimmer |
| 3 | 016.png → 034.png | Kitchen | 360 Orbit (gentle arc) | gentle orbit past the counter and cabinetry, bright even lighting, premium finish, steady cinematic motion, photorealistic, stable geometry, no warping, no morphing | pending | Arc from dining vantage into kitchen straight-on |
| 4 | 010.png (single — CONTROL) | King bedroom (baseline) | Dolly In | slow dolly-in toward the made bed, eye-level, smooth steady gimbal, soft window light, calm steady motion, photorealistic, stable geometry, no warping, no morphing | pending | Single-frame control vs paired clips — first/last-frame experiment |
| 5 | 048.png → 049.png | Hot tub — water beat | Handheld (slow pan) | slow pan across the hot tub water toward the patio dining beyond, gentle steady motion, soft daylight, photorealistic, stable geometry, no warping, no morphing | pending | Pan across water with a real destination |
| 6 | 054.png → 053.png | Dusk closer — lit house + steps | Dolly In | slow dolly forward through the evening yard toward the stone steps and the glowing lit house, eye-level, smooth steady motion, warm evening light, photorealistic, stable geometry, no warping, no morphing | pending | Both dusk, same axis; string lights = thin-line watch |

**First/last-frame doctrine (this batch's experiment):** Kling 3.0 first+last frame
mode; pairs must share light regime + screen direction (no 180 flips) + plausible
single move between them. Verify every pair at full-res in the composer before
firing. Clip 4 stays single-frame as the control — paired-vs-unpaired quality
comparison goes to the Findings Log and decides house doctrine.

**Montage map:** (045→042) → (005→033) → (016→034) → 010 → (048→049) → (054→053). Forward momentum on every cut
(approach → through the door → into the home → out to the amenity); light arcs
day → dusk ("arrive in daylight, stay into the evening").

**Full-set scout findings (2026-07-03, CS sheets):** no flamingo-free pool frame
exists — pool beat dropped, hot tub is the water beat. Two light regimes (day +
dedicated twilight set 012/013/051/053/054) — twilight shoot = invested-host
signal, X-Factor candidate. Five sleeping spaces (king, slat-wall queen, iron-bed,
twin-queen boho, bunk room) — market as group/family property. Arch mirror in
011/030/031/035 (avoided); glossy closets 020 (avoided); Universal TV splash in
multiple living frames.

**Batch cost estimate:** 45 credits actual (6 clips × 7.5 credits — Kling 3.0 std, 5s, sound off; preflight verified). Account at fire: 1,210 credits, Plus plan.

## Job registry (T3 — fired 2026-07-03)

| Clip | Job ID | Start media_id | End media_id |
|---|---|---|---|
| 1 (045→042) | 80c291c1-1991-420f-880e-a8a7991b2d0a | acdbc218-da2f-4a6e-ab1f-5bdafed45f59 | 312e12b5-8519-4df7-8329-47e42c57588b |
| 2 (005→033) | 6c62b2a7-0f06-4473-9e61-1c4664cd70ca | 87e80d1a-6061-47e8-b74e-617578d8a1e7 | ea326eac-10e5-4421-94c9-e5f127d83bb5 |
| 3 (016→034) | a783f217-670d-4a4d-8d89-ac4854362320 | 76f41344-6cd5-4cb6-9beb-fcad8d49f4c0 | 8247db7a-df8a-4eaf-a9f5-1abb8565db21 |
| 4 (010 ctrl) | 3612aaed-3357-45b7-a571-0cea0860f521 | b5606700-e34c-4818-ae7e-7937cbea4db2 | — |
| 5 (048→049) | 01f6fefd-5791-48fa-8411-4698790f2f90 | 83c5377f-12c8-49b7-957b-a400ed0c16c3 | c0c008ab-b011-46f4-bc20-0978a9362157 |
| 6 (054→053) | e35fd15c-8559-48ff-a5d1-195d02769351 | 0b45f07a-759e-42fe-a5f9-f20852b94584 | 4443cf84-2e77-474f-a306-5f97d8d94213 |

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
