# S140 S139 Gallery Refresh Publish

## Objective

Package and publish the S139 low-angle impact close-up artifacts so the latest contact-focused cinematic gate can be inspected externally.

## Inputs

- Shot directory: `build/shots/s139_low_angle_impact_closeup`
- Shot report: `docs/reports/cinematic_low_angle_impact_closeup_s139.md`
- Review manifest: `build/shots/s139_low_angle_impact_closeup/review/review_manifest.json`

## Scope

- Build the artifact inspection package for S139.
- Build a self-contained static gallery under the S139 shot directory.
- Publish the gallery through the existing CFTunnel helper.
- Verify local and public `index.html` plus `assets/shot.gif`.
- Update README and the cinematic roadmap after publish.

## Non-Goals

- Do not rerun the S139 Blender gate unless a required artifact is missing.
- Do not stop older gallery tunnels.
- Do not add gallery publishing to default `ctest`.

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s139_low_angle_impact_closeup --out docs\reports\cinematic_artifact_package_s140.md
python tools\build_cinematic_gallery.py build\shots\s139_low_angle_impact_closeup --package docs\reports\cinematic_artifact_package_s140.md --out build\shots\s139_low_angle_impact_closeup\gallery --report docs\reports\cinematic_static_gallery_s140.md
python tools\publish_cinematic_gallery.py build\shots\s139_low_angle_impact_closeup\gallery --port 8801 --cftunnel --manifest build\shots\s139_low_angle_impact_closeup\gallery\publish_manifest_s140.json --report docs\reports\cinematic_gallery_publish_s140.md --timeout-seconds 120
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
