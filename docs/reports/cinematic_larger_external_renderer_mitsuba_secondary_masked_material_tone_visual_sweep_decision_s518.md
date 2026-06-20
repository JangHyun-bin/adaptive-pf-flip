# S518 Material Tone Visual Sweep Decision

Generated UTC: `2026-06-20T19:48:08Z`

## Inputs

- Sweep summary: `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/material_tone_hybrid_sweep_summary.json`
- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Channel mask: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`
- Baseline triage: `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_full48_visual_triage_s517.md`

## Sweep Gate

- Status: `ready`
- Variants rendered: `4`
- Frames per variant: `8`
- SPP: `4`
- Export failures: `0`
- Validation failures: `0`
- Render failures: `0`
- Target-gap missing references: `0`

## Candidate Target Gap

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| --- | ---: | ---: | ---: |
| `mt9_sharp_key` | `74.17916160300926` | `104.49566872427984` | `193` |
| `mt10_dim_secondary_strong_key` | `74.17561623906893` | `104.48653549382716` | `195` |
| `mt11_soft_water_bright` | `74.18103997878086` | `104.49457304526749` | `194` |
| `mt12_highlight_cut` | `74.17765817901234` | `104.48696887860082` | `194` |

Decision-gallery best candidate remained `S445_GL3_SurfaceGlint` with max gap MAD `23.9334458590535`.

## Visual Response Metrics

Metrics were computed over each candidate render preview directory.

| Candidate | Mean Luma Mean | Contrast Mean | P95 Mean | P99 Mean | Bright >= 220 Mean | Highlight >= 245 Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `mt9_sharp_key` | `166.262291` | `171.528875` | `168.091175` | `191.133300` | `0.005070` | `0.004474` |
| `mt10_dim_secondary_strong_key` | `166.259703` | `170.242775` | `168.100200` | `191.133300` | `0.005067` | `0.004479` |
| `mt11_soft_water_bright` | `166.263562` | `169.260825` | `168.091175` | `191.124275` | `0.005069` | `0.004481` |
| `mt12_highlight_cut` | `166.260079` | `169.367275` | `168.010800` | `191.124275` | `0.005064` | `0.004482` |

S517 full48 baseline had mean luminance `166.265066`, mean contrast `168.351346`, mean bright ratio `0.004165`, and mean highlight ratio `0.003620`.

## Decision

S518 proves that the S322 secondary masked export can still pass the full material-tone pipeline: the export, validation, real Mitsuba render, target-gap comparison, and decision-gallery stages all completed.

The visual improvement is too small to justify a longer render from these exact candidates. The S322 XML material/key-light modulation slightly raises highlight occupancy, but the P95 band stays near `168`, mean luminance stays near `166`, and all variants remain visually close to the flat S515 baseline.

The next move should not be another S322 material-only sweep. Use the stronger low-frequency/screen-card visual response path from S488 as the next real-backend input, then render a bounded 16-frame SPP4 sample and publish it for visual review.

## Next

Run a real Mitsuba backend command-adapter sample from the strongest S488 low-frequency/native screen-card export, then compare it against S515 and the existing S508/S509 low-frequency backend sample.
