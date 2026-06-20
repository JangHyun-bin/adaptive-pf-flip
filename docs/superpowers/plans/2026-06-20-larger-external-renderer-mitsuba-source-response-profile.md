# Larger External Renderer: Mitsuba Source Response Profile

Status: complete

## Goal

Make the current best CR21-like target-free visual response reproducible without
remembering a long argument list.

## Scope

- Add `--profile cr21` to `tools/apply_mitsuba_source_region_response.py`.
- Keep the existing default behavior unchanged.
- Encode the S388 CR21 source-region response settings as a named profile.
- Regenerate CR21 output through the profile.
- Verify pixel parity against S388.
- Compare the profiled output against the renderer target gap.

## Validation

- `python -m py_compile tools\apply_mitsuba_source_region_response.py`
- S401 profile generation: `ready`, `8` frames
- Pixel parity against S388 CR21:
  - max channel diff: `0`
  - mean channel diff: `0.0`
- S401 target-gap comparison:
  - max target MAD: `23.552905092592592`
  - mean target MAD: `18.657217962319958`

## Result

`--profile cr21` reproduces S388 exactly and remains much closer to the target
than the recent native-only candidates. This is still a post-render source
response, not a true Mitsuba BSDF replacement, but it is target-free at runtime
and gives the project a stable visual baseline.

## Decision

Use `--profile cr21` as the current inspectable visual baseline while native
Mitsuba material work continues. The next renderer work should either publish
this profile gallery for review or move the CR21 response into a renderer-native
pass with a stronger material model.
