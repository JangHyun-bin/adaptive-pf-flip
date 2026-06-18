# Cinematic Visual Review Triage

Generated UTC: `2026-06-18T22:03:28Z`
Gallery manifest: `build/shots/s127_nonboxed_falling_water/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s127_nonboxed_falling_water/gallery/publish_manifest_s128.json`
Shot summary: `build/shots/s127_nonboxed_falling_water/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_nonboxed_falling_water` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `7886592` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8149 |
| local assets/shot.gif | `HEAD` | 200 | 24072256 |
| public index.html | `GET` | 200 | 8149 |
| public assets/shot.gif | `HEAD` | 200 | 24072256 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 24072256 | `1280 x 720` |
| Contact sheet | `yes` | 439009 | `1008 x 660` |
| Baseline comparison | `yes` | 391431 | `1322 x 487` |
| Focus comparison | `yes` | 244049 | `1322 x 337` |
| Secondary depth comparison | `yes` | 462508 | `1562 x 486` |
| Ripple readability comparison | `yes` | 240222 | `1322 x 351` |
| Focus sheet | `no` | 462889 | `1308 x 549` |
| Secondary depth sheet | `no` | 618333 | `1308 x 720` |
| Ripple readability sheet | `no` | 500296 | `1308 x 579` |
| Temporal diff sheet | `no` | 207292 | `1008 x 660` |
| Review manifest | `no` | 22527 | `n/a` |
| Render summary | `no` | 51225 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `90.662` | visual balance |
| mean contrast | `232.222` | visual balance |
| mean bright ratio | `0.004` | highlight presence |
| secondary min inside ratio | `1.000` | composition risk |
| secondary mean screen y | `0.505` | composition |
| secondary mean crop ratio | `1.000` | secondary visibility |
| secondary mean depth span | `11.049` | depth layering |
| secondary channel depth delta | `0.496` | channel separation |
| ripple edge mean | `25.757` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000110.
- Secondary channel depth separation is modest: mean channel depth delta is 0.496.
- Rendered secondary channels end with no droplet channel contribution.
- S127 contact/comparison sheets show a clear improvement over S126: the falling source has a rounded/tapered lower edge instead of a flat rectangular slab, and secondary framing remains fully inside frame.
- The shot still reads as stylized contained water because the vertical side/background bands and broad enclosure remain visible, especially in late frames.
- Water/spray diagnostics remain stable: visual, focus, secondary-depth, ripple, temporal, and secondary framing gates all pass, so the next change can target scene art direction rather than gate recovery.

## Decision

Select S130 environment/depth-context pass: reduce visible side-wall/enclosure bands and add stronger large-scale depth context around the non-boxed falling-water scene while preserving the S127 gates and public gallery workflow.

## Next

S130 should reduce visible side-wall/enclosure bands and add stronger large-scale depth context around the non-boxed falling-water scene while preserving the S127 gates and public gallery workflow.
