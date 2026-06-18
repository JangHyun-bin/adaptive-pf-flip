# Cinematic Visual Review Triage

Generated UTC: `2026-06-18T22:29:23Z`
Gallery manifest: `build/shots/s130_environment_depth_context/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s130_environment_depth_context/gallery/publish_manifest_s131.json`
Shot summary: `build/shots/s130_environment_depth_context/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_environment_depth_context` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `7886592` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8152 |
| local assets/shot.gif | `HEAD` | 200 | 22521818 |
| public index.html | `GET` | 200 | 8152 |
| public assets/shot.gif | `HEAD` | 200 | 22521818 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 22521818 | `1280 x 720` |
| Contact sheet | `yes` | 409156 | `1008 x 660` |
| Baseline comparison | `yes` | 396561 | `1322 x 487` |
| Focus comparison | `yes` | 250428 | `1322 x 337` |
| Secondary depth comparison | `yes` | 458120 | `1562 x 486` |
| Ripple readability comparison | `yes` | 240489 | `1322 x 351` |
| Focus sheet | `no` | 443324 | `1308 x 549` |
| Secondary depth sheet | `no` | 578114 | `1308 x 720` |
| Ripple readability sheet | `no` | 481814 | `1308 x 579` |
| Temporal diff sheet | `no` | 189658 | `1008 x 660` |
| Review manifest | `no` | 22777 | `n/a` |
| Render summary | `no` | 51672 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `84.677` | visual balance |
| mean contrast | `234.278` | visual balance |
| mean bright ratio | `0.002` | highlight presence |
| secondary min inside ratio | `1.000` | composition risk |
| secondary mean screen y | `0.497` | composition |
| secondary mean crop ratio | `1.000` | secondary visibility |
| secondary mean depth span | `11.020` | depth layering |
| secondary channel depth delta | `0.518` | channel separation |
| ripple edge mean | `22.430` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000081.
- Secondary channel depth separation is modest: mean channel depth delta is 0.518.
- Rendered secondary channels end with no droplet channel contribution.
- S130 preserves all current cinematic gates while slightly softening the floor/world contrast and broadening the mist/scattering context.
- The public gallery still reads as a contained shot in late frames because the continuous vertical water column and side bands dominate the composition.
- The next visible improvement should alter the falling-water silhouette itself rather than only tuning lighting, haze, or gallery presentation.

## Decision

Select S133 falling-source silhouette breakup pass: change the non-boxed falling-water scene/preset so the upper falling mass is broken into staggered rounded lobes with less continuous vertical side-wall structure, then run a 36-frame Blender comparison against S130.

## Next

S133 should implement the falling-source silhouette breakup pass and run a 36-frame Blender comparison against S130.
