# S187 S186 Gallery Publish

Date: 2026-06-19

## Goal

Package and publish the S186 water surface continuity render so it can be
reviewed through a public Cloudflare quick tunnel URL.

## Inputs

- Shot directory: `build/shots/s186_water_surface_continuity_stabilized`
- Comparison sheet:
  `build/shots/s186_water_surface_continuity_stabilized/comparison/comparison_sheet.png`
- Comparison summary:
  `build/shots/s186_water_surface_continuity_stabilized/comparison/comparison_summary.json`
- S186 gate report: `docs/reports/cinematic_water_surface_continuity_s186.md`

## Commands

```powershell
python tools\build_bridge_cinematic_gallery.py build\shots\s186_water_surface_continuity_stabilized --out build\shots\s186_water_surface_continuity_stabilized\gallery --comparison-sheet build\shots\s186_water_surface_continuity_stabilized\comparison\comparison_sheet.png --comparison-summary build\shots\s186_water_surface_continuity_stabilized\comparison\comparison_summary.json --comparison-label "S183 vs S186 Comparison" --title "S186 Water Surface Continuity" --keyframes 3 --report docs\reports\cinematic_water_surface_continuity_gallery_s187.md
```

```powershell
python tools\publish_cinematic_gallery.py build\shots\s186_water_surface_continuity_stabilized\gallery --port 8826 --cftunnel --manifest build\shots\s186_water_surface_continuity_stabilized\gallery_publish_s187_manifest.json --report docs\reports\cinematic_gallery_publish_s187.md --timeout-seconds 120
```

## Result

- Public URL: `https://prizes-inventory-plaintiff-violations.trycloudflare.com`
- Local URL: `http://127.0.0.1:8826`
- HTTP server PID: `131436`
- cloudflared PID: `90272`
- Gallery report:
  `docs/reports/cinematic_water_surface_continuity_gallery_s187.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s187.md`

Fresh public checks:

- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/index.html`:
  HTTP `200`, `5519` bytes
- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/assets/shot.gif`:
  HTTP `200`, `23627133` bytes
- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/assets/comparison.png`:
  HTTP `200`, `2573439` bytes
- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/assets/keyframe_00.png`:
  HTTP `200`, `1134451` bytes

## Next

S188 should triage the public S186 gallery and choose whether to accept the
surface continuity pass or rebound overlay strength.
