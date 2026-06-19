# S184 S183 Gallery Publish

Date: 2026-06-19

## Goal

Package and publish the S183 secondary direct visibility gate render so it can
be reviewed through a public Cloudflare quick tunnel URL.

## Inputs

- Shot directory: `build/shots/s183_secondary_direct_visibility_gate`
- Comparison sheet:
  `build/shots/s183_secondary_direct_visibility_gate/comparison/comparison_sheet.png`
- Comparison summary:
  `build/shots/s183_secondary_direct_visibility_gate/comparison/comparison_summary.json`
- S183 gate report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_s183.md`

## Commands

```powershell
python tools\build_bridge_cinematic_gallery.py build\shots\s183_secondary_direct_visibility_gate --out build\shots\s183_secondary_direct_visibility_gate\gallery --comparison-sheet build\shots\s183_secondary_direct_visibility_gate\comparison\comparison_sheet.png --comparison-summary build\shots\s183_secondary_direct_visibility_gate\comparison\comparison_summary.json --comparison-label "S180 vs S183 Comparison" --title "S183 Secondary Direct Visibility Gate" --keyframes 3 --report docs\reports\cinematic_secondary_direct_visibility_gate_gallery_s184.md
```

```powershell
python tools\publish_cinematic_gallery.py build\shots\s183_secondary_direct_visibility_gate\gallery --port 8825 --cftunnel --manifest build\shots\s183_secondary_direct_visibility_gate\gallery_publish_s184_manifest.json --report docs\reports\cinematic_gallery_publish_s184.md --timeout-seconds 120
```

## Result

- Public URL: `https://cove-grades-tba-tags.trycloudflare.com`
- Local URL: `http://127.0.0.1:8825`
- HTTP server PID: `126776`
- cloudflared PID: `57320`
- Gallery report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_gallery_s184.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s184.md`

Fresh public checks:

- `https://cove-grades-tba-tags.trycloudflare.com/index.html`: HTTP `200`,
  `5532` bytes
- `https://cove-grades-tba-tags.trycloudflare.com/assets/shot.gif`: HTTP `200`,
  `24035658` bytes
- `https://cove-grades-tba-tags.trycloudflare.com/assets/comparison.png`: HTTP
  `200`, `1289990` bytes
- `https://cove-grades-tba-tags.trycloudflare.com/assets/keyframe_00.png`: HTTP
  `200`, `1159220` bytes

## Next

S185 should triage the public S183 gallery and choose whether to accept the
direct-secondary visibility gate or tune one more secondary material pass.
