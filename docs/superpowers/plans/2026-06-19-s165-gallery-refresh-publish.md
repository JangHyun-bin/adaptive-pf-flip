# S166 S165 Gallery Refresh Publish

## Objective

Package and publish the S165 source-slab de-emphasis cinematic gate so the
current source-shape/composition adjustment can be inspected externally before
the next visual triage.

## Inputs

- Shot output: `build/shots/s165_source_slab_deemphasis`
- Shot report: `docs/reports/cinematic_source_slab_deemphasis_s165.md`
- Baseline comparison: `build/shots/s162_establishing_scale_composition/review/review_manifest.json`

## Scope

- Build an artifact package report for the S165 GIF and review sheets.
- Build a self-contained static gallery under the S165 shot directory.
- Publish the gallery with the existing Cloudflare quick tunnel path.
- Verify local and public `index.html` plus `assets/shot.gif`.
- Record the public URL and verification status in checked-in reports.

## Non-Goals

- Do not re-render S165 unless the existing artifacts fail validation.
- Do not select the next visible adjustment until S165 is publicly inspectable.
- Do not stop existing Cloudflare tunnel processes from earlier milestones.

## Candidate Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s165_source_slab_deemphasis --report docs\reports\cinematic_artifact_package_s166.md
python tools\build_cinematic_gallery.py build\shots\s165_source_slab_deemphasis --report docs\reports\cinematic_static_gallery_s166.md
python tools\publish_cinematic_gallery.py build\shots\s165_source_slab_deemphasis\gallery --port 8820 --cloudflare --report docs\reports\cinematic_gallery_publish_s166.md
```

## Acceptance Gate

- Artifact package report is generated and links all expected S165 review assets.
- Static gallery manifest and `index.html` are generated under the S165 shot output.
- Local and public gallery URLs return HTTP 200 for `index.html` and `assets/shot.gif`.
- The public URL is recorded in the S166 publish report.
