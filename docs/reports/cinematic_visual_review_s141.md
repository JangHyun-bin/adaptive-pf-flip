# Cinematic Visual Review Triage

Generated UTC: `2026-06-18T23:40:13Z`
Gallery manifest: `build/shots/s139_low_angle_impact_closeup/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s139_low_angle_impact_closeup/gallery/publish_manifest_s140.json`
Shot summary: `build/shots/s139_low_angle_impact_closeup/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_low_angle_impact_closeup` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `7886592` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8151 |
| local assets/shot.gif | `HEAD` | 200 | 22204480 |
| public index.html | `GET` | 200 | 8151 |
| public assets/shot.gif | `HEAD` | 200 | 22204480 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 22204480 | `1280 x 720` |
| Contact sheet | `yes` | 426128 | `1008 x 660` |
| Baseline comparison | `yes` | 414292 | `1322 x 487` |
| Focus comparison | `yes` | 299306 | `1322 x 394` |
| Secondary depth comparison | `yes` | 555760 | `1562 x 539` |
| Ripple readability comparison | `yes` | 279099 | `1322 x 394` |
| Focus sheet | `no` | 547404 | `1308 x 666` |
| Secondary depth sheet | `no` | 691967 | `1308 x 810` |
| Ripple readability sheet | `no` | 563350 | `1308 x 666` |
| Temporal diff sheet | `no` | 205758 | `1008 x 660` |
| Review manifest | `no` | 22707 | `n/a` |
| Render summary | `no` | 51491 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `85.886` | visual balance |
| mean contrast | `198.028` | visual balance |
| mean bright ratio | `0.001` | highlight presence |
| secondary min inside ratio | `0.595` | composition risk |
| secondary mean screen y | `0.754` | composition |
| secondary mean crop ratio | `0.753` | secondary visibility |
| secondary mean depth span | `6.523` | depth layering |
| secondary channel depth delta | `0.387` | channel separation |
| ripple edge mean | `22.485` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000049.
- Secondary channel depth separation is modest: mean channel depth delta is 0.387.
- Rendered secondary channels end with no droplet channel contribution.
- S139 makes the contact band larger and more stable than S136 while preserving all numeric review gates and public gallery asset checks.
- The remaining visual issue is timing/composition: early gallery frames spend too much screen time on a calm pool before the impact becomes readable, and small source fragments still touch the top edge in some later frames.
- S139 secondary framing remains gated but is closest to the lower frame edge in early frames, so the next pass should improve perceived timing without narrowing the frame further.

## Decision

Select S142 impact-timed review window: add a runner/render path that can render a later cache window from the same simulation, so the cinematic artifact starts closer to visible impact while keeping S139 framing and gates.

## Next

S142 should add an impact-timed cinematic window option and run a checked-in 36-frame Blender comparison against S139.
