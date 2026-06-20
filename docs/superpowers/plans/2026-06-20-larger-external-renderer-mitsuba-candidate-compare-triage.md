# Larger External Renderer: Mitsuba Candidate Compare Triage

Status: complete

## Goal

Use the S403 comparison board to choose the next renderer development branch.

## Evidence

- S403 compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_candidate_compare_ss1_kl1_cr21_s403.md`
- S403 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_candidate_compare_ss1_kl1_cr21_publish_s403.md`
- S404 triage report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_candidate_compare_visual_triage_s404.md`

## Decision

Keep `SS1_Native` as the native baseline and `S401_CR21_Profile` as the visual
response reference. Do not promote `KL1`, and do not continue broad scalar
water/light sweeps as the next branch.

## Next

Start S405 as a bounded CR21-native migration pass. The goal is not to use the
target image at runtime; it is to make a renderer-side/source-secondary response
candidate that can be compared against SS1 and the CR21 profile using the S403
gallery pattern.
