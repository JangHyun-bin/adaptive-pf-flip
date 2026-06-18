# S137 S136 Gallery Refresh Publish

## Objective

Package and publish the S136 offscreen-source impact framing artifacts so the current best cinematic result can be inspected through the static gallery and Cloudflare quick tunnel.

## Inputs

- Shot directory: `build/shots/s136_offscreen_source_impact_framing`
- Shot report: `docs/reports/cinematic_offscreen_source_impact_framing_s136.md`
- Review manifest: `build/shots/s136_offscreen_source_impact_framing/review/review_manifest.json`

## Scope

- Build a checked report with GIF, contact sheet, comparison sheet, focus sheet, secondary-depth sheet, and ripple-readability sheet links.
- Build a self-contained static gallery under the S136 shot directory.
- Publish the gallery through the existing CFTunnel helper.
- Verify local and public `index.html` plus `assets/shot.gif`.
- Update README and the cinematic roadmap after publish.

## Non-Goals

- Do not rerun the S136 Blender gate unless a required artifact is missing.
- Do not stop older gallery tunnels in this milestone.
- Do not add gallery publishing to default `ctest`.

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s136_offscreen_source_impact_framing --out docs\reports\cinematic_artifact_package_s137.md
python tools\build_cinematic_gallery.py build\shots\s136_offscreen_source_impact_framing --package docs\reports\cinematic_artifact_package_s137.md --out build\shots\s136_offscreen_source_impact_framing\gallery --report docs\reports\cinematic_static_gallery_s137.md
python tools\publish_cinematic_gallery.py build\shots\s136_offscreen_source_impact_framing\gallery --port 8800 --cftunnel --manifest build\shots\s136_offscreen_source_impact_framing\gallery\publish_manifest_s137.json --report docs\reports\cinematic_gallery_publish_s137.md --timeout-seconds 120
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
