# S404 Mitsuba Candidate Compare Visual Triage

Generated UTC: `2026-06-20T08:30:00Z`

Source gallery: `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/gallery/index.html`

Public review URL: `https://scholar-page-wednesday-soviet.trycloudflare.com/index.html`

## Inputs

| Candidate | Role | Evidence |
| --- | --- | --- |
| `Target` | Visual reference | `build/shots/s328_mitsuba_renderer_target_preview/renderer_target` |
| `C1E` | Bridge/reference composite | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1e/depth_aware_secondary_composite_summary.json` |
| `SS1_Native` | Current native baseline | `build/shots/s357_mitsuba_secondary_3d_soft_ss1/actual_render/mitsuba_render.json` |
| `KL1` | S400 least-bad water/light variant | `build/shots/s400_mitsuba_water_light_kl1/actual_render/mitsuba_render.json` |
| `S401_CR21_Profile` | Current target-free source-response profile | `build/shots/s401_mitsuba_source_response_profile_cr21/source_region_response_summary.json` |

## Numeric Anchors

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| `KL1` | 19.222773517875513 | 23.988705632716048 | 226 |
| `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| `C1E` | 11.464264805169753 | 14.389824459876543 | 196 |

## Visual Findings

- `SS1_Native` is still the correct native baseline. It is stable and avoids
  obvious post-process artifacts, but source highlights and dark secondary
  response are too muted versus the target.
- `KL1` should not be promoted. It keeps the native structure but does not solve
  the missing source/secondary response and loses the S400 numeric ranking.
- `S401_CR21_Profile` is the strongest inspectable visual response. It restores
  the source/dark-secondary contrast much better than the native candidates,
  especially in middle and late frames.
- `S401_CR21_Profile` is not yet the final physical renderer answer. The source
  region reads closer to the target, but some upper source and secondary regions
  still look like a separate response layer instead of water/secondary transport
  produced inside the renderer.

## Decision

Keep two baselines:

- Native baseline: `SS1_Native`
- Visual response reference: `S401_CR21_Profile`

Do not spend the next pass on broad water roughness, water transmittance, or
global key-light sweeps. The next useful work is a renderer-side/native response
pass that tries to reproduce the CR21 source and dark-secondary behavior without
using target images.

## Next

S405 should start a bounded CR21-native migration pass:

- preserve SS1 camera, water, sidecar, and secondary material as the native
  control;
- reuse the target-free CR21 response profile as the visual contract;
- add an inspectable renderer-side/source-secondary response candidate rather
  than another global scalar sweep;
- compare it against `SS1_Native`, `S401_CR21_Profile`, and the target through
  the same S403 gallery/report flow.
