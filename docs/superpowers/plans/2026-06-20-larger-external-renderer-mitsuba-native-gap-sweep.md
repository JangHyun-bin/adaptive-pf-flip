# S332 Mitsuba Native Gap Sweep

## Goal

Run a small renderer-native Mitsuba material/secondary sweep and promote the
candidate that best reduces the measured S328 target gap.

## Scope

- Add `tools/summarize_mitsuba_native_gap_sweep.py`.
- Render candidate B with lower background radiance, lower water alpha, and a
  smaller/lighter secondary proxy setup.
- Render candidate C with a denser secondary proxy setup.
- Compare both candidates against the S328 accepted target.
- Rank S330 baseline, S331 native pass, S332 B, and S332 C.
- Publish the best candidate B gap gallery through Cloudflare Tunnel.

## Candidate Settings

Candidate B:

- `background-radiance 0.16,0.23,0.32`
- `water-alpha 0.014`
- `secondary-proxy-limit 384`
- `secondary-proxy-radius 0.10`
- `secondary-opacity 0.16`

Candidate C:

- `background-radiance 0.17,0.24,0.33`
- `water-alpha 0.012`
- `secondary-proxy-limit 512`
- `secondary-proxy-radius 0.09`
- `secondary-opacity 0.24`

## Outputs

- Sweep summary:
  `build/shots/s332_mitsuba_native_gap_sweep_summary/sweep_summary.json`
- Sweep report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_sweep_summary_s332.md`
- Best candidate B gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_sweep_b_gap_s332.md`
- Best candidate B publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_sweep_b_publish_s332.md`
- Public URL:
  `https://also-ringtone-compilation-only.trycloudflare.com`

## Acceptance

- Candidate B export, render, and gap reports are `ready`.
- Candidate C export, render, and gap reports are `ready`.
- Sweep summary is `ready`.
- Best candidate is `sweep_b`.
- Candidate B max gap mean absolute diff is `67.67647762345679`.
- Candidate B mean gap mean absolute diff is `37.73105774176955`.
- Candidate B improves over S331 max gap `85.7207773919753`.
- Public `index.html` and `assets/shot.gif` return HTTP `200`.
