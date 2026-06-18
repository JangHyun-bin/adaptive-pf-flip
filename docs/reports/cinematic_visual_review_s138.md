# Cinematic Visual Review Triage

Generated UTC: `2026-06-18T23:16:53Z`
Gallery manifest: `build/shots/s136_offscreen_source_impact_framing/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s136_offscreen_source_impact_framing/gallery/publish_manifest_s137.json`
Shot summary: `build/shots/s136_offscreen_source_impact_framing/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_offscreen_source_impact_framing` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `7886592` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8158 |
| local assets/shot.gif | `HEAD` | 200 | 24080794 |
| public index.html | `GET` | 200 | 8158 |
| public assets/shot.gif | `HEAD` | 200 | 24080794 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 24080794 | `1280 x 720` |
| Contact sheet | `yes` | 453493 | `1008 x 660` |
| Baseline comparison | `yes` | 417309 | `1322 x 487` |
| Focus comparison | `yes` | 281053 | `1322 x 372` |
| Secondary depth comparison | `yes` | 521488 | `1562 x 521` |
| Ripple readability comparison | `yes` | 270011 | `1322 x 394` |
| Focus sheet | `no` | 541525 | `1308 x 621` |
| Secondary depth sheet | `no` | 701943 | `1308 x 780` |
| Ripple readability sheet | `no` | 587797 | `1308 x 666` |
| Temporal diff sheet | `no` | 218194 | `1008 x 660` |
| Review manifest | `no` | 22893 | `n/a` |
| Render summary | `no` | 52322 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `88.266` | visual balance |
| mean contrast | `218.528` | visual balance |
| mean bright ratio | `0.001` | highlight presence |
| secondary min inside ratio | `1.000` | composition risk |
| secondary mean screen y | `0.611` | composition |
| secondary mean crop ratio | `1.000` | secondary visibility |
| secondary mean depth span | `7.450` | depth layering |
| secondary channel depth delta | `0.479` | channel separation |
| ripple edge mean | `23.182` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000089.
- Secondary channel depth separation is modest: mean channel depth delta is 0.479.
- Rendered secondary channels end with no droplet channel contribution.
- S136 reframes the S133 source-breakup scene toward an impact shot: the source is pushed to the top edge while spray, foam, ripple, and pool contact occupy more of the readable frame.
- The public gallery checks are healthy and the S136 numeric gates remain passing: visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates are all green in the shot report.
- The main remaining visual weakness is composition: the upper water mass is still partially visible in early frames and the contact surface still reads flatter than a cinematic low-angle impact close-up.

## Decision

Select S139 low-angle impact close-up framing: keep the S136 source-breakup scene, move the camera lower/closer toward the contact band, crop the upper source fully out of frame, and preserve secondary/ripple readability gates.

## Next

S139 should add a low-angle impact close-up preset and run a checked-in 36-frame Blender comparison against S136.
