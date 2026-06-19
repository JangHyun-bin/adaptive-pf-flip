# Cinematic Visual Review Triage

Generated UTC: `2026-06-19T01:03:26Z`
Gallery manifest: `build/shots/s148_foreground_water_thickness_refraction/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s148_foreground_water_thickness_refraction/gallery/publish_manifest_s149.json`
Shot summary: `build/shots/s148_foreground_water_thickness_refraction/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_foreground_water_thickness_refraction` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `10515456` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8165 |
| local assets/shot.gif | `HEAD` | 200 | 24719294 |
| public index.html | `GET` | 200 | 8165 |
| public assets/shot.gif | `HEAD` | 200 | 24719294 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 24719294 | `1280 x 720` |
| Contact sheet | `yes` | 469052 | `1008 x 660` |
| Baseline comparison | `yes` | 436098 | `1322 x 487` |
| Focus comparison | `yes` | 325357 | `1322 x 394` |
| Secondary depth comparison | `yes` | 590377 | `1562 x 539` |
| Ripple readability comparison | `yes` | 294903 | `1322 x 394` |
| Focus sheet | `no` | 602966 | `1308 x 666` |
| Secondary depth sheet | `no` | 768775 | `1308 x 810` |
| Ripple readability sheet | `no` | 609598 | `1308 x 666` |
| Temporal diff sheet | `no` | 241085 | `1008 x 660` |
| Review manifest | `no` | 23286 | `n/a` |
| Render summary | `no` | 53142 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `91.710` | visual balance |
| mean contrast | `200.278` | visual balance |
| mean bright ratio | `0.002` | highlight presence |
| secondary min inside ratio | `1.000` | composition risk |
| secondary mean screen y | `0.648` | composition |
| secondary mean crop ratio | `0.975` | secondary visibility |
| secondary mean depth span | `7.942` | depth layering |
| secondary channel depth delta | `0.328` | channel separation |
| ripple edge mean | `27.259` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000153.
- Secondary channel depth separation is modest: mean channel depth delta is 0.328.
- Rendered secondary channels end with no droplet channel contribution.
- S148 keeps S145 timing/framing and strengthens foreground water-body depth cues with 14-layer scattering, depth strength 0.62, and rim strength 0.58 while preserving all review gates.
- Mean luminance remains stable at 91.71 and ripple edge mean remains high at 27.26, so the thickness pass did not wash out contact breakup.
- The public gallery still shows visible upper-edge source fragments in early frames; this is now more distracting than water-material depth.

## Decision

Select S151 source-edge cleanup framing pass.

## Next

Add an inherited S148 preset that crops or de-emphasizes the upper source region through camera/source-window tuning while preserving S148 water thickness, secondary framing, ripple readability, temporal, camera, and visual gates.
