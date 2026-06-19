# Cinematic Visual Review Triage

Generated UTC: `2026-06-19T02:23:32Z`
Gallery manifest: `build/shots/s157_contact_foam_sheet_continuity/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s157_contact_foam_sheet_continuity/gallery/publish_manifest_s158.json`
Shot summary: `build/shots/s157_contact_foam_sheet_continuity/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_contact_foam_sheet_continuity` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `10515456` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8157 |
| local assets/shot.gif | `HEAD` | 200 | 25140731 |
| public index.html | `GET` | 200 | 8157 |
| public assets/shot.gif | `HEAD` | 200 | 25140731 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 25140731 | `1280 x 720` |
| Contact sheet | `yes` | 454680 | `1008 x 660` |
| Baseline comparison | `yes` | 296703 | `1322 x 487` |
| Focus comparison | `yes` | 228823 | `1322 x 394` |
| Secondary depth comparison | `yes` | 414412 | `1562 x 539` |
| Ripple readability comparison | `yes` | 224507 | `1322 x 394` |
| Focus sheet | `no` | 581791 | `1308 x 666` |
| Secondary depth sheet | `no` | 749042 | `1308 x 810` |
| Ripple readability sheet | `no` | 602274 | `1308 x 666` |
| Temporal diff sheet | `no` | 225067 | `1008 x 660` |
| Review manifest | `no` | 23154 | `n/a` |
| Render summary | `no` | 52265 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `91.450` | visual balance |
| mean contrast | `190.944` | visual balance |
| mean bright ratio | `0.001` | highlight presence |
| secondary min inside ratio | `0.994` | composition risk |
| secondary mean screen y | `0.689` | composition |
| secondary mean crop ratio | `0.954` | secondary visibility |
| secondary mean depth span | `7.909` | depth layering |
| secondary channel depth delta | `0.532` | channel separation |
| ripple edge mean | `27.357` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000235.
- Secondary channel depth separation is modest: mean channel depth delta is 0.532.
- Rendered secondary channels end with no droplet channel contribution.
- S157 broadens flow-aligned contact foam strokes while preserving S154 mist integration, source-window framing, and all review gates.
- Mean luminance remains stable at 91.45 and ripple edge mean remains high at 27.36, so foam continuity did not wash out contact-surface detail.
- The current shot has accumulated several renderer-side improvements; the remaining gap to cinematic scale is now more about larger physical event scale and richer simulation-driven secondary motion than another small material tweak.

## Decision

Select S160 large-event cinematic scale gate.

## Next

Run a bounded larger-event cinematic gate from the current S157 render look, using a larger grid/event preset or warm-cache-friendly large scene settings, and compare against S157 for runtime, framing, secondary readability, and visual gates.
