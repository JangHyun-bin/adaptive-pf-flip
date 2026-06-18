# S128 S127 Gallery Refresh And Publish

## Objective

Package and publish the S127 non-boxed falling-water review artifacts so the current cinematic result can be inspected in a browser and through a Cloudflare quick tunnel.

## Scope

- Build a static gallery from `build/shots/s127_nonboxed_falling_water`.
- Package the S127 GIF, contact sheet, and comparison sheets into a checked-in report.
- Publish the gallery with `tools/publish_cinematic_gallery.py`.
- Verify local and public HTTP access for `index.html` and `assets/shot.gif`.
- Do not rerender the cinematic shot in this slice.

## Command

```powershell
python tools\package_cinematic_artifacts.py build\shots\s127_nonboxed_falling_water --out docs\reports\cinematic_artifact_package_s128.md
python tools\build_cinematic_gallery.py build\shots\s127_nonboxed_falling_water --out build\shots\s127_nonboxed_falling_water\gallery --report docs\reports\cinematic_static_gallery_s128.md
python tools\publish_cinematic_gallery.py build\shots\s127_nonboxed_falling_water\gallery --cloudflare --manifest build\shots\s127_nonboxed_falling_water\gallery\publish_manifest_s128.json
```

## Acceptance Gate

- Artifact package report is generated.
- Static gallery report is generated.
- Gallery manifest includes `shot.gif`, contact sheet, and comparison sheets.
- Local `index.html` returns HTTP 200.
- Local `assets/shot.gif` returns HTTP 200.
- Public `index.html` returns HTTP 200.
- Public `assets/shot.gif` returns HTTP 200.

## Verification

```powershell
python -m py_compile tools\package_cinematic_artifacts.py tools\build_cinematic_gallery.py tools\publish_cinematic_gallery.py
git diff --check
```
