# Cinematic Visual Review Triage

Generated UTC: `2026-06-19T01:30:47Z`
Gallery manifest: `build/shots/s151_source_edge_cleanup_framing/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s151_source_edge_cleanup_framing/gallery/publish_manifest_s152.json`
Shot summary: `build/shots/s151_source_edge_cleanup_framing/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_source_edge_cleanup_framing` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `10515456` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8155 |
| local assets/shot.gif | `HEAD` | 200 | 24770818 |
| public index.html | `GET` | 200 | 8155 |
| public assets/shot.gif | `HEAD` | 200 | 24770818 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 24770818 | `1280 x 720` |
| Contact sheet | `yes` | 469775 | `1008 x 660` |
| Baseline comparison | `yes` | 434697 | `1322 x 487` |
| Focus comparison | `yes` | 319485 | `1322 x 394` |
| Secondary depth comparison | `yes` | 591090 | `1562 x 539` |
| Ripple readability comparison | `yes` | 293156 | `1322 x 394` |
| Focus sheet | `no` | 590781 | `1308 x 666` |
| Secondary depth sheet | `no` | 762346 | `1308 x 810` |
| Ripple readability sheet | `no` | 606208 | `1308 x 666` |
| Temporal diff sheet | `no` | 238736 | `1008 x 660` |
| Review manifest | `no` | 23047 | `n/a` |
| Render summary | `no` | 52001 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `91.625` | visual balance |
| mean contrast | `199.000` | visual balance |
| mean bright ratio | `0.002` | highlight presence |
| secondary min inside ratio | `0.994` | composition risk |
| secondary mean screen y | `0.689` | composition |
| secondary mean crop ratio | `0.954` | secondary visibility |
| secondary mean depth span | `7.909` | depth layering |
| secondary channel depth delta | `0.532` | channel separation |
| ripple edge mean | `27.465` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000233.
- Secondary channel depth separation is modest: mean channel depth delta is 0.532.
- Rendered secondary channels end with no droplet channel contribution.
- S151 reduces the lead-in by rendering source frames 12-47 and tightening the lower camera while all visual, focus, secondary-depth, ripple, temporal, camera, and secondary-framing gates pass.
- Secondary framing remains robust with mean inside ratio 0.9998 and ripple edge mean improves to 27.47, so the tighter framing did not lose contact detail.
- The remaining visible artifact is that the secondary particles still read as bead-like dots in several frames rather than integrated mist/spray/foam.

## Decision

Select S154 secondary bead de-emphasis and mist integration pass.

## Next

Add an inherited S151 preset that reduces bead-like secondary radius/brightness while strengthening soft mist/streak integration for spray and foam, preserving S151 framing, water thickness, ripple, temporal, and secondary-depth gates.
