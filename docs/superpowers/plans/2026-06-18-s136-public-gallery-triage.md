# S138 S136 Public Gallery Triage

## Objective

Review the S136 public gallery and pick the next visible cinematic adjustment from the artifact evidence rather than guessing from local logs.

## Inputs

- Public gallery: `https://mighty-eligibility-described-tops.trycloudflare.com`
- Gallery manifest: `build/shots/s136_offscreen_source_impact_framing/gallery/gallery_manifest.json`
- Publish manifest: `build/shots/s136_offscreen_source_impact_framing/gallery/publish_manifest_s137.json`
- Shot summary: `build/shots/s136_offscreen_source_impact_framing/shot_summary.json`

## Scope

- Summarize local/public gallery coverage.
- Confirm all required visual artifacts remain present.
- Record numeric render/review gates from the S136 shot summary.
- Add visual findings from the public gallery and local contact/comparison sheets.
- Select the next concrete S139 visible adjustment.

## Non-Goals

- Do not rerun the S136 Blender shot.
- Do not stop existing gallery tunnels.
- Do not make the next visual adjustment in this milestone.

## Command

```powershell
python tools\summarize_cinematic_gallery_review.py build\shots\s136_offscreen_source_impact_framing\gallery\gallery_manifest.json --publish build\shots\s136_offscreen_source_impact_framing\gallery\publish_manifest_s137.json --out docs\reports\cinematic_visual_review_s138.md --decision "Select the next visible shot adjustment from the S136 public gallery evidence." --next "S139 should implement the selected visual adjustment with a checked-in preset or scene change plus a 36-frame Blender comparison gate."
```

## Acceptance Gate

- The triage report is generated and checked in.
- Public gallery checks in the publish manifest are all HTTP 200.
- The report lists specific visual findings, not just numeric gates.
- The next S139 target is concrete enough to implement without re-planning.

## Verification

```powershell
python -m py_compile tools\summarize_cinematic_gallery_review.py
git diff --check
```
