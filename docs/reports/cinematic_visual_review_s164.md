# S164 S162 Public Gallery Visual Triage

## Summary

- Status: `ok`
- Public gallery: `https://edmonton-prospect-cure-actions.trycloudflare.com`
- Local gallery: `http://127.0.0.1:8819`
- Source shot: `build/shots/s162_establishing_scale_composition`
- Baseline comparison: `build/shots/s160_large_event_scale_gate`
- Selected next milestone: S165 source-slab silhouette de-emphasis scene pass.

## Public Asset Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8819/index.html` | GET | 200 | 8158 |
| `http://127.0.0.1:8819/assets/shot.gif` | HEAD | 200 | 26333525 |
| `https://edmonton-prospect-cure-actions.trycloudflare.com/index.html` | GET | 200 | 8158 |
| `https://edmonton-prospect-cure-actions.trycloudflare.com/assets/shot.gif` | HEAD | 200 | 26333525 |

## Numeric Gate Summary

| Metric | S160 | S162 |
| --- | ---: | ---: |
| Source window | 16..55 | 16..55 |
| Selected source frames | 40 | 40 |
| GIF bytes | 26170768 | 26333525 |
| Visual mean luminance | 93.297 | 93.396 |
| Visual min contrast | 112.0 | 189.0 |
| Secondary mean inside ratio | 0.9995 | 0.9999 |
| Secondary min inside ratio | 0.9870 | 0.9957 |
| Secondary mean screen Y | 0.6887 | 0.6896 |
| Ripple edge mean | 28.478 | 29.617 |
| Focus mean luminance | 90.175 | 91.130 |
| Blender render seconds | 414.96 | 408.81 |

All S162 visual, temporal, focus, secondary-depth, secondary-framing, ripple-readability, and camera-stability gates passed.

## Visual Findings

- S162 opens the impact-pool read relative to S160 without losing secondary framing or ripple readability.
- The wider composition improves the broad water-surface context, especially in mid and late frames.
- The remaining visible blocker is the top source silhouette: the source-breakup water body can still read as a ceiling-like slab instead of a naturally falling curtain.
- Bead-like secondary particles did not regress materially; the mist/secondary integration remains acceptable.
- Another render-only camera widening pass is unlikely to solve the slab silhouette. The next pass should change the source shape or source-window/source-scene contract.

## Decision

Proceed with S165: add a source-slab silhouette de-emphasis scene/preset. The implementation should attack the physical/source initialization first, not only crop the camera:

- Add a source-breakup variant with thinner upper lobes and more vertical gaps.
- Expose it through the exporter scene list and cinematic preset config.
- Run a dry-run/probe before the full Blender gate.
- Compare against S162 and preserve the existing QA gates where feasible.

## Verification

```powershell
git diff --check
```
