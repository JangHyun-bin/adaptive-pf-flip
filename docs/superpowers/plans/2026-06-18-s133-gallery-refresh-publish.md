# S134 S133 Gallery Refresh Publish

## Objective

Package and publish the S133 falling-source silhouette breakup shot so the current result can be inspected externally.

## Inputs

- Shot directory: `build/shots/s133_falling_source_silhouette_breakup`
- Shot report: `docs/reports/cinematic_falling_source_silhouette_breakup_s133.md`
- Previous public gallery: `https://italiano-anaheim-empty-colored.trycloudflare.com`

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s133_falling_source_silhouette_breakup --out docs\reports\cinematic_artifact_package_s134.md
python tools\build_cinematic_gallery.py build\shots\s133_falling_source_silhouette_breakup --package docs\reports\cinematic_artifact_package_s134.md --out build\shots\s133_falling_source_silhouette_breakup\gallery --report docs\reports\cinematic_static_gallery_s134.md
python tools\publish_cinematic_gallery.py build\shots\s133_falling_source_silhouette_breakup\gallery --port 8799 --cftunnel --manifest build\shots\s133_falling_source_silhouette_breakup\gallery\publish_manifest_s134.json --report docs\reports\cinematic_gallery_publish_s134.md --timeout-seconds 120
```

## Acceptance Gate

- Artifact package records GIF, contact sheet, comparison sheets, and review manifests.
- Static gallery has `index.html`, `gallery_manifest.json`, and copied assets.
- Publisher verifies local/public `index.html` and `assets/shot.gif`.
- README and roadmap point to the next S133 public-gallery triage or visible shot-shape adjustment.

## Verification

```powershell
python -m py_compile tools\package_cinematic_artifacts.py tools\build_cinematic_gallery.py tools\publish_cinematic_gallery.py
git diff --check
```
