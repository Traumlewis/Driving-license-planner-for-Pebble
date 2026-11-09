# Project preferences

- Maintain all six platforms through the five device projects. Use release.json and tools/sync_release.py for versions and credits.
- The current development version is 3.8.42; continue 3.8.43, 3.8.44, etc., following the owner’s version numbering.
- Source updates to GitHub are authorized. Create or publish a GitHub Release, or promote a test build to a normal release, only when the owner explicitly requests it. Source pushes must not trigger release publication.
- Provide a ready-to-test combined PBW after app changes. Test filenames must include (DEV). Use tools/build_all.py --output to keep test binaries outside the tracked release/ directory.
- Preserve user appointments, theory checkboxes, counters and extra minutes during updates. Normal release developer is Traumlewis; credits remain (Idee by Traumlewis | Code by Codex).

- Language packs: generate with tools/sync_release.py; see docs/DEV-3.8.42.md. Short translated strings use rolling buffers: copy text retained across draw callbacks. German is the built-in fallback; long English explanations remain bundled in this prototype.
