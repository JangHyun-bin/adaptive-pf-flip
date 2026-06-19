# S178 S177 Gallery Refresh Publish

## Objective

Package and publish the S177 surface reflection breakup render for public
inspection.

## Inputs

- Shot directory: `build/shots/s177_surface_reflection_breakup`
- Comparison sheet:
  `build/shots/s177_surface_reflection_breakup/comparison/comparison_sheet.png`
- Comparison summary:
  `build/shots/s177_surface_reflection_breakup/comparison/comparison_summary.json`

## Commands

```powershell
python tools\build_bridge_cinematic_gallery.py build\shots\s177_surface_reflection_breakup --out build\shots\s177_surface_reflection_breakup\gallery --comparison-sheet build\shots\s177_surface_reflection_breakup\comparison\comparison_sheet.png --comparison-summary build\shots\s177_surface_reflection_breakup\comparison\comparison_summary.json --comparison-label "S173 vs S177 Comparison" --title "S177 Surface Reflection Breakup" --keyframes 3 --report docs\reports\cinematic_surface_reflection_breakup_gallery_s178.md
```

```powershell
python tools\publish_cinematic_gallery.py build\shots\s177_surface_reflection_breakup\gallery --port 8823 --cftunnel --manifest build\shots\s177_surface_reflection_breakup\gallery_publish_s178_manifest.json --report docs\reports\cinematic_gallery_publish_s178.md --timeout-seconds 120
```

## Result

- Local URL: `http://127.0.0.1:8823`
- Public URL: `https://alloy-mailman-right-gay.trycloudflare.com`
- HTTP server PID: `115328`
- cloudflared PID: `87340`
- Gallery report: `docs/reports/cinematic_surface_reflection_breakup_gallery_s178.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s178.md`

Checks:

- `http://127.0.0.1:8823/index.html`: HTTP `200`, `5514` bytes
- `http://127.0.0.1:8823/assets/shot.gif`: HTTP `200`, `24084190` bytes
- `https://alloy-mailman-right-gay.trycloudflare.com/index.html`: HTTP `200`, `5514` bytes
- `https://alloy-mailman-right-gay.trycloudflare.com/assets/shot.gif`: HTTP `200`, `24084190` bytes

## Next

S179 should triage the public gallery and decide whether the strip breakup
bounds are acceptable or need one more tuning pass.
