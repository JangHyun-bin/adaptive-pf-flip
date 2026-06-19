# S153 S151 Public Gallery Visual Triage

## Objective

Review the S151 public gallery evidence and choose the next concrete visible cinematic adjustment after the source-edge cleanup framing pass.

## Inputs

- Gallery manifest: `build/shots/s151_source_edge_cleanup_framing/gallery/gallery_manifest.json`
- Publish manifest: `build/shots/s151_source_edge_cleanup_framing/gallery/publish_manifest_s152.json`
- Public gallery: `https://canal-hint-carbon-face.trycloudflare.com`
- S151 report: `docs/reports/cinematic_source_edge_cleanup_framing_s151.md`

## Scope

- Summarize gallery/publish coverage and current visual gates.
- Record visible strengths and remaining visible problems from the current gallery.
- Pick exactly one next cinematic look-dev adjustment that can be implemented as a bounded preset/render pass.

## Non-Goals

- Do not re-render the shot.
- Do not change simulation physics during triage.
- Do not stop existing gallery tunnels.

## Candidate Command

```powershell
python tools\summarize_cinematic_gallery_review.py build\shots\s151_source_edge_cleanup_framing\gallery\gallery_manifest.json --publish build\shots\s151_source_edge_cleanup_framing\gallery\publish_manifest_s152.json --out docs\reports\cinematic_visual_review_s153.md --finding "S151 reduces early upper-source distraction with source frames 12-47 and tighter lower camera framing while preserving all review gates." --decision "Select the next visible adjustment from the S151 public gallery." --next "TBD by S153 triage."
```

## Acceptance Gate

- `docs/reports/cinematic_visual_review_s153.md` exists.
- The report records local/public gallery asset checks.
- The report names one next milestone with a practical scope and comparison baseline.

## Verification

```powershell
git diff --check
```
