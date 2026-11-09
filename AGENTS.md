# Project preferences

- Maintain all six platforms through the five device projects. Use release.json and tools/sync_release.py for versions and credits.
- The current development version is 3.8.47; continue 3.8.48, 3.8.49, etc., following the owner’s version numbering.
- Source updates to GitHub are authorized. Create or publish a GitHub Release, or promote a test build to a normal release, only when the owner explicitly requests it. Source pushes must not trigger release publication.
- Provide a ready-to-test combined PBW after app changes. Test filenames must include (DEV). Use tools/build_all.py --output to keep test binaries outside the tracked release/ directory.
- Preserve user appointments, theory checkboxes, counters and extra minutes during updates. Normal release developer is Traumlewis; credits remain (Idee by Traumlewis | Code by Codex).

- Language packs: generate with tools/sync_release.py; see docs/DEV-3.8.47.md. Short translated strings use rolling buffers: copy text retained across draw callbacks. Only the selected DE/EN menu packet is persisted. A small loading/emergency fallback and longer explanations remain bundled. Native menu literals use generated LK_ IDs; restore canonical text with generate_language_pack.restore_project before editing it, then synchronize.

- Repository packet layout: Packs/Germany/Languages/<app-version>/. Germany denotes Germany’s training rules, while de/en denote interface languages. Export with tools/export_language_packs.py after synchronization. The phone downloads the version-pinned selected packet from GitHub and caches only that packet; full developer fixtures live in tools/language-packets.json outside the phone bundle. Publish matching versioned packets before distributing a build.

- Native menu packets use Packs/Germany; phone settings languages use Packs/App/Languages. The owner explicitly requested removal of the old German compatibility directory. Do not recreate it. The settings list and translations use the dynamic settings-v1 catalogue; an English fallback remains bundled. New settings-only languages require data updates, not PBW builds. Additional watch languages/decoders/glyphs are deferred. See tools/register_settings_language.py and preserve custom catalogue entries.
