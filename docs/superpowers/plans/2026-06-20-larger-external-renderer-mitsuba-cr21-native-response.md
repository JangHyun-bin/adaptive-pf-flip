# Larger External Renderer: Mitsuba CR21 Native Response Migration

Status: complete

## Goal

Start migrating the CR21 source/dark-secondary response from post-render profile
logic toward renderer-side candidates while keeping runtime target-free.

## Scope

- Refactor source-response classification into a reusable helper.
- Add a mask-source builder for CR21 highlight, dark-secondary, channel-band,
  and response-union evidence.
- Use those mask sources in bounded native renderer candidates.
- Render, score, and publish the candidates against SS1 and CR21.

## Result

The tooling path is useful, but the screen-space migration candidates are not
good enough to promote.

- Best native S405 max target MAD: `23.98830825617284`
- SS1 max target MAD: `23.951853137860084`
- S401 CR21 max target MAD: `23.552905092592592`

## Decision

Keep the new mask-source tool and CR21 classifier helper. Do not continue
screen-space card/sprite tuning as the main CR21 replacement path.

## Next

S406 should use the S405 masks as evidence for a material/AOV response pass
rather than directly rendering the masks as camera-facing cards.
