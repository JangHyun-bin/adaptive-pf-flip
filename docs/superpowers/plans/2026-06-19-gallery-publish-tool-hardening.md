# S226 Gallery Publish Tool Hardening

## Goal

Fix the publish-tool issue found during S225 so future cftunnel publishes do not accidentally validate stale URLs or the wrong local gallery server.

## Scope

- Harden `tools/publish_cinematic_gallery.py`.
- Keep the public S225 tunnel running.
- Do not change gallery content or cinematic presets.

## Implementation

- Truncate process logs on each new publish process instead of appending to old logs.
- Make `choose_port` check the requested bind address.
- Avoid `SO_REUSEADDR` on Windows so an occupied port is treated as occupied.

## Validation

- `python -m py_compile tools\publish_cinematic_gallery.py`
- Inline Python regression smoke for occupied-port skip and stale-log truncation.
- Local publish smoke from occupied port `18899`, verifying that the tool selected `18900`.
- Manifest-based stop for the test server.

## Result

The publisher now chooses a fresh port when the requested port is already occupied and no longer scans stale tunnel URLs from previous log files.
