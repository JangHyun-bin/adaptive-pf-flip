# S143 S142 Gallery Refresh Publish

## Objective

Package and publish the S142 impact-timed window artifacts so the latest cinematic gate can be inspected externally.

## Inputs

- Shot directory: `build/shots/s142_impact_timed_window`
- Shot report: `docs/reports/cinematic_impact_timed_window_s142.md`
- Review manifest: `build/shots/s142_impact_timed_window/review/review_manifest.json`

## Scope

- Build the artifact inspection package for S142.
- Build a self-contained static gallery under the S142 shot directory.
- Publish the gallery through the existing CFTunnel helper.
- Verify local and public `index.html` plus `assets/shot.gif`.
- Update README and the cinematic roadmap after publish.

## Non-Goals

- Do not rerun the S142 Blender gate unless a required artifact is missing.
- Do not stop older gallery tunnels.
- Do not add gallery publishing to default `ctest`.

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s142_impact_timed_window --out docs\reports\cinematic_artifact_package_s143.md
python tools\build_cinematic_gallery.py build\shots\s142_impact_timed_window --package docs\reports\cinematic_artifact_package_s143.md --out build\shots\s142_impact_timed_window\gallery --report docs\reports\cinematic_static_gallery_s143.md
python tools\publish_cinematic_gallery.py build\shots\s142_impact_timed_window\gallery --port 8802 --cftunnel --manifest build\shots\s142_impact_timed_window\gallery\publish_manifest_s143.json --report docs\reports\cinematic_gallery_publish_s143.md --timeout-seconds 120
```

## Acceptance Gate

- Artifact package report is generated.
- Static gallery has `index.html`, `gallery_manifest.json`, and copied media assets.
- Publish report records local and public URLs.
- Publish checks return HTTP 200 for local/public `index.html` and `assets/shot.gif`.

## Verification

```powershell
python -m py_compile tools\package_cinematic_artifacts.py tools\build_cinematic_gallery.py tools\publish_cinematic_gallery.py
git diff --check
```
