# S358 Mitsuba Native Visual Review

## Goal

Build a compact visual review package for the current native Mitsuba candidates
before increasing secondary particle strength again.

## Inputs

- Target and C1E depth-aware composite:
  `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1e/depth_aware_secondary_composite_summary.json`
- MW7 no-secondary native baseline:
  `build/shots/s351_mitsuba_native_material_mw7/actual_render/mitsuba_render.json`
- SD4 depth/material sidecar candidate:
  `build/shots/s356_mitsuba_secondary_3d_depth_sd4/actual_render/mitsuba_render.json`
- SS1 sidecar-soft baseline:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/actual_render/mitsuba_render.json`

## Changes

- Added `tools/build_mitsuba_candidate_compare_gallery.py`.
- Generated side-by-side strips and a GIF for:
  `Target | C1E | MW7 | SD4 | SS1`.
- Wrote the S358 review report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_visual_review_s358.md`.

## Result

The gallery is ready:

- Summary:
  `build/shots/s358_mitsuba_native_visual_review/candidate_compare_gallery.json`
- Gallery:
  `build/shots/s358_mitsuba_native_visual_review/gallery/index.html`
- Comparison GIF:
  `build/shots/s358_mitsuba_native_visual_review/gallery/assets/comparison.gif`
- Public quick-tunnel preview:
  `https://cash-equity-weekend-statutes.trycloudflare.com/index.html`

The visual read is clear: MW7, SD4, and SS1 keep the hard numeric gate close to
the current best native baseline, but all three are still too dim and low
contrast compared with the target/C1E reference. The sidecar path is now safe
enough to tune, but it still needs an appearance bridge rather than another
blind opacity increase.

## Next

Run a target-informed visibility pass for native secondary particles:

- preserve SS1/SD4's hard max-target gate,
- lift sidecar contrast only in projected secondary regions,
- keep water/background controls fixed,
- compare against S350 C1E and MW7 with both numeric metrics and visual strips.
