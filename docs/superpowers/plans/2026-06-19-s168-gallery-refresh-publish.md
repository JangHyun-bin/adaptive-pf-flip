# S169 S168 Gallery Refresh Publish

## Objective

Package and publish the S168 water depth and foreground separation gate so the
new depth/readability tuning can be inspected externally before the next visual
triage.

## Inputs

- Shot output: `build/shots/s168_water_depth_foreground_separation`
- Shot report: `docs/reports/cinematic_water_depth_foreground_separation_s168.md`
- Baseline comparison: `build/shots/s165_source_slab_deemphasis/review/review_manifest.json`

## Scope

- Build an artifact package report for the S168 GIF and review sheets.
- Build a self-contained static gallery under the S168 shot directory.
- Publish the gallery with the existing Cloudflare quick tunnel path.
- Verify local and public `index.html` plus `assets/shot.gif`.
- Record the public URL and verification status in checked-in reports.

## Non-Goals

- Do not re-render S168 unless the existing artifacts fail validation.
- Do not select the next visible adjustment until S168 is publicly inspectable.
- Do not stop existing Cloudflare tunnel processes from earlier milestones.

## Candidate Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s168_water_depth_foreground_separation --out docs\reports\cinematic_artifact_package_s169.md
python tools\build_cinematic_gallery.py build\shots\s168_water_depth_foreground_separation --package docs\reports\cinematic_artifact_package_s169.md --out build\shots\s168_water_depth_foreground_separation\gallery --report docs\reports\cinematic_static_gallery_s169.md
python tools\publish_cinematic_gallery.py build\shots\s168_water_depth_foreground_separation\gallery --port 8821 --cftunnel --manifest build\shots\s168_water_depth_foreground_separation\gallery_publish_s169_manifest.json --report docs\reports\cinematic_gallery_publish_s169.md
```

## Acceptance Gate

- Artifact package report is generated and links all expected S168 review assets.
- Static gallery manifest and `index.html` are generated under the S168 shot output.
- Local and public gallery URLs return HTTP 200 for `index.html` and `assets/shot.gif`.
- The public URL is recorded in the S169 publish report.
