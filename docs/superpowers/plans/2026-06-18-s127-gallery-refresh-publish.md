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
python tools\publish_cinematic_gallery.py build\shots\s127_nonboxed_falling_water\gallery --cftunnel --manifest build\shots\s127_nonboxed_falling_water\gallery\publish_manifest_s128.json
```

Actual publish command used `--cftunnel`, matching the current script CLI:

```powershell
python tools\publish_cinematic_gallery.py build\shots\s127_nonboxed_falling_water\gallery --port 8797 --cftunnel --manifest build\shots\s127_nonboxed_falling_water\gallery\publish_manifest_s128.json --report docs\reports\cinematic_gallery_publish_s128.md --timeout-seconds 120
```

## Result

S128 passed and published the S127 gallery.

- Artifact package: `docs/reports/cinematic_artifact_package_s128.md`
- Static gallery report: `docs/reports/cinematic_static_gallery_s128.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s128.md`
- Gallery manifest: `build/shots/s127_nonboxed_falling_water/gallery/gallery_manifest.json`
- Publish manifest: `build/shots/s127_nonboxed_falling_water/gallery/publish_manifest_s128.json`
- Local URL: `http://127.0.0.1:8797`
- Public URL: `https://fields-diary-motivated-record.trycloudflare.com`
- HTTP server PID: `80172`
- cloudflared PID: `19816`

Verified HTTP checks:

- local `index.html`: HTTP 200, `8149` bytes
- local `assets/shot.gif`: HTTP 200, `24072256` bytes
- public `index.html`: HTTP 200, `8149` bytes
- public `assets/shot.gif`: HTTP 200, `24072256` bytes

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

## Next

S129 should review the S127 public gallery and choose the next concrete visible improvement from current evidence.
