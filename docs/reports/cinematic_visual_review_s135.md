# Cinematic Visual Review Triage

Generated UTC: `2026-06-18T22:52:01Z`
Gallery manifest: `build/shots/s133_falling_source_silhouette_breakup/gallery/gallery_manifest.json`
Publish manifest: `build/shots/s133_falling_source_silhouette_breakup/gallery/publish_manifest_s134.json`
Shot summary: `build/shots/s133_falling_source_silhouette_breakup/gallery/assets/shot_summary.json`

## Current Shot

| Field | Value |
| --- | --- |
| status | `ok` |
| renderer | `blender` |
| preset | `dam_break_falling_source_silhouette_breakup` |
| grid | `32 x 40 x 26` |
| frames | `36` |
| samples | `12` |
| comparison sources | `2` |
| export particles | `218880` |
| validated particles | `7886592` |

## Publish Checks

| Endpoint | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| local index.html | `GET` | 200 | 8160 |
| local assets/shot.gif | `HEAD` | 200 | 21375618 |
| public index.html | `GET` | 200 | 8160 |
| public assets/shot.gif | `HEAD` | 200 | 21375618 |

## Artifact Coverage

- Required visual artifacts present: `6 / 6`
- Total gallery artifacts: `12`

| Artifact | Required | Size | Dimensions |
| --- | --- | ---: | --- |
| Shot GIF | `yes` | 21375618 | `1280 x 720` |
| Contact sheet | `yes` | 412447 | `1008 x 660` |
| Baseline comparison | `yes` | 385119 | `1322 x 487` |
| Focus comparison | `yes` | 244324 | `1322 x 337` |
| Secondary depth comparison | `yes` | 448312 | `1562 x 486` |
| Ripple readability comparison | `yes` | 230246 | `1322 x 351` |
| Focus sheet | `no` | 440640 | `1308 x 549` |
| Secondary depth sheet | `no` | 576594 | `1308 x 720` |
| Ripple readability sheet | `no` | 472664 | `1308 x 579` |
| Temporal diff sheet | `no` | 184457 | `1008 x 660` |
| Review manifest | `no` | 22994 | `n/a` |
| Render summary | `no` | 52582 | `n/a` |

## Numeric Triage

| Metric | Value | Notes |
| --- | ---: | --- |
| visual gate | `true` | pass/fail |
| focus gate | `true` | pass/fail |
| secondary depth gate | `true` | pass/fail |
| ripple readability gate | `true` | pass/fail |
| temporal highlight gate | `true` | pass/fail |
| mean luminance | `82.399` | visual balance |
| mean contrast | `233.444` | visual balance |
| mean bright ratio | `0.001` | highlight presence |
| secondary min inside ratio | `1.000` | composition risk |
| secondary mean screen y | `0.499` | composition |
| secondary mean crop ratio | `1.000` | secondary visibility |
| secondary mean depth span | `7.464` | depth layering |
| secondary channel depth delta | `0.474` | channel separation |
| ripple edge mean | `20.244` | surface detail |
| ripple highlight ratio | `0.000` | surface highlight control |

## Visual Findings

- Water-body focus highlights are subdued: focus bright-ratio mean is 0.000076.
- Secondary channel depth separation is modest: mean channel depth delta is 0.474.
- Rendered secondary channels end with no droplet channel contribution.
- S133 keeps all cinematic gates passing and changes the upper water source from a flatter slab into staggered rounded lobes.
- The public gallery still reads as contained in late frames because the camera continues to show the whole upper falling mass instead of letting water enter from outside the frame.
- The next visible improvement should be shot-framing driven: hide or mostly crop the source generator while keeping the impact pool, spray, and lower water surface in frame.

## Decision

Select S136 offscreen-source impact framing pass: keep the S133 source-breakup scene, but move the cinematic camera/target/FOV so the upper source is mostly out of frame and the shot focuses on water entering the frame and impacting the pool.

## Next

S136 should implement the offscreen-source impact framing pass and run a 36-frame Blender comparison against S133.
