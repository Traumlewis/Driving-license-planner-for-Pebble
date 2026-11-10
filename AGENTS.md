# Project preferences

- Maintain all six platforms through the five device projects. Use release.json and tools/sync_release.py for versions and credits.
- The current release version is 3.8.55, explicitly approved by the owner on 2026-11-10; continue development at 3.8.56, 3.8.57, etc., following the owner’s version numbering.
- Source updates to GitHub are authorized. Create or publish a GitHub Release, or promote a test build to a normal release, only when the owner explicitly requests it. Source pushes must not trigger release publication.
- Provide a ready-to-test combined PBW after app changes. Test filenames must include (DEV). Use tools/build_all.py --output to keep test binaries outside the tracked release/ directory.
- Keep (DEV) out of the native version, visible guide version and package versionLabel. Use three numeric version components. Text-package/documentation-only edits do not inherently require a new app version or PBW. Never overwrite already published PBWs, release checksums or release assets.
- Preserve user appointments, theory checkboxes, counters and extra minutes during updates. Normal release developer is Traumlewis; credits remain (Idee by Traumlewis | Code by Codex).

- Language packs: generate with tools/sync_release.py; see docs/DEV-3.8.55.md. Short translated strings use eight rolling buffers: copy text retained across draw callbacks. Only the selected LP5 watch packet is persisted; it includes menus and long explanations. A small emergency/loading fallback and shared codec remain bundled. Freeze tools/watch-codec-v7.json and tools/watch-schema.json when adding translations; use tools/register_watch_language.py without rebuilding. Native menu literals use generated LK_ IDs; restore canonical text with generate_language_pack.restore_project before editing it, then synchronize.

- Repository packet layout: Packs/App/Languages for dynamic settings and generic LP5 watch packets; Only the current compatibility variant is published; legacy LP3 folders and prior watch variants were retired at the owner’s explicit request. Export with tools/export_language_packs.py after synchronization. The phone downloads the schema/codec-compatible selected packet from GitHub and caches only that packet; full developer fixtures live in tools/language-packets.json outside the phone bundle. Publish matching versioned packets before distributing a build.

- All new language packets use Packs/App/Languages; publish only the current variant; do not recreate archived Germany LP3 folders or old watch variants. The owner explicitly requested removal of the old German compatibility directory. Do not recreate it. The settings list and translations use the dynamic settings-v1 catalogue; an English fallback remains bundled. New settings-only languages require data updates, not PBW builds. DE/EN/ES/FR/IT/PT/NL/PL/DA/SV/FI/CS/HU/RO/SK/HR/SL/ET/LV/LT/MT/GA/EL/BG watch languages use the generic decoder. Additional compatible watch languages need only data; unsupported glyphs or schema/codec changes may require a build. See tools/register_settings_language.py and preserve custom catalogue entries. The v7 resource was explicitly migrated for twenty-four languages in 3.8.55 after the owner requested the final six EU languages; publish only its current watchPacks variant and never retrain on registration.

- Compact app persistence starts at 3.8.50: src/c/compact_storage.c/h keeps keys and the booking journal, reads both raw and packed records, migrates in place at startup and skips unchanged values. Keep all five copies identical. Do not install pre-3.8.50 builds directly on packed records: build/run tools/build_legacy_restore.py first, which restores legacy values before an old build. Source defaults must always be COMPACT_WRITE_DEFAULT 1; only the temporary restore-helper build uses 0. See docs/DEV-3.8.50.md and tests/compact_storage_test.c. The compact application-data format remains unchanged; 3.8.55 migrates the separate selected language packet from LP4 to LP5.

- Real watch languages use IDs 0–23; use unregistered test ID 42 for post-build generic-decoder verification. Production catalogue download budget remains 60KB; lab HTTP adapters should match it.

- Greek/Cyrillic UI uses seven resource-backed Open Sans Condensed variants, selected by a Greek/Cyrillic autonym in the selected packet metadata. Latin languages retain existing system Gothic fonts. Keep script_fonts.c/h identical across projects. Descriptors load lazily and remain valid until app exit (TextLayer retains GFont pointers); do not unload them during a language swap. Font source/license live under resources/fonts. Adding translations must not regenerate or expand shipped glyph ranges.

- LP5 uses seven frozen resource-backed prefix-code books over shared BPE tokens. The packet chooses its book in header byte 3; the encoder picks the smallest result and expands uncoded intermediate tokens to coded children. Every book covers all bytes. Keep the 24-byte header, 2,560-byte cap and 16-byte persistence metadata; never retrain during registration. See docs/DEV-3.8.55.md for the explicit v7 migration and canonical grouped training recipe.

- Current-only language support policy: explicitly authorized by the owner after 3.8.55. tools/export_language_packs.py removes non-current watch compatibility variants after successful export. Keep all 24 current settings/source/watch packs and the frozen v7 codec/schema. Historical training files are developer references, not live compatibility packs. No app/PBW version change is needed for catalogue cleanup; the existing 3.8.55 DEV PBW remains valid. See docs/language-pack-support.md.

- Release 3.8.55 was explicitly authorized and published on 2026-11-10 using the exact tested DEV PBW bytes under the regular filename; SHA256 a42d6790c7f9e715c3d739d8e4dc853e4db8a4bb822ed0b73f64c86b7fa4bea9. Its one-time publication workflow and transport parts were removed from main after publication. Keep the normal workflow_dispatch-only release workflow; ordinary source updates must never publish releases. Future releases require another explicit owner request.

## Device and design reference

| Native target | Watches | Project | Display |
| --- | --- | --- | --- |
| emery | Time 2 | projects/time2 | 200 x 228 |
| flint | Core 2 Duo | projects/core2duo | 144 x 168 |
| gabbro | Round 2 | projects/round2 | 260 x 260 round |
| basalt | Time / Time Steel | projects/time-pebble2 | 144 x 168 |
| diorite | Pebble 2 / Pebble 2 SE | projects/time-pebble2 | 144 x 168 |
| chalk | Time Round | projects/timeround | 180 x 180 round |

- One combined PBW covers these six targets. Buttons work on every target; Time 2 and Round 2 additionally support touch. The original Pebble/Steel (aplite) are not currently supported.
- Preserve the approved navy/cyan design and device-specific layouts. Keep headings visually centred, circular submenu icon/title geometry distinct from the home layout, hard scroll limits without rubber-banding, readable first/last rows and restored selection/scroll position when returning from a submenu. Keep class-specific vehicle icons and trailers behind the towing vehicle.
- Preserve Settings and Explanations grouping. Changing class from Settings is not first-time setup and must not force the previous-licence wizard. Phone settings refresh automatically when opened.

## Behaviour to preserve

- Training rules cover Germany's 16 licence classes and their training profiles, regardless of interface language. Austria/Switzerland rule packs were discussed but are not implemented. Do not present 24 interface languages as 24 countries' training regulations.
- New appointments default to reminders 60 and 30 minutes beforehand; reminder 2 can be disabled. Keep ten-minute snooze, alarms while the app is closed, and optional Timeline integration. Completed lessons are booked only after confirmation.
- Practical lesson types without a fixed minimum use whole-unit entry; do not offer irrelevant extra-minute editing for their progress counters. Their bar is empty at zero whole units and full from one. Required practical types retain 45-minute units and five-minute steps, with extra minutes accumulated by class/type; theory units are 90 minutes.
- Theory checkmarks contribute to the corresponding GS/ZS totals. Linked appointments must not double-count a checked topic. Manual edits affect only manually added units; protected checkmark units can be removed only through the topic checklist.
- User appointments, class/profile, topic checkmarks, manual units, remainders and selected language must survive upgrades. Back up before migrations and compare meaningful state afterwards. Never erase persistent watch data or uninstall the planner as a routine test shortcut.

## Editing and downloading translations

- Current compatibility key: 37bc2f9e-869b4728; schema 935079838; codec 2258323240; LP5/shared-bpe-v1. The live index contains only this variant and 24 watch languages (IDs 0-23).
- index.json, <locale>/settings.json and watch/<compatibility>/<locale>.json under Packs/App/Languages are downloaded. <locale>/watch-source.json is the editable source, not the transmitted watch packet. The phone caches the selected settings packet and selected watch packet separately; the watch persists one chosen watch packet. Phone and watch languages may differ until Apply to watch.
- For text-only changes, keep internal keys, schema limits and printf placeholders stable. Re-encode the watch source and update the catalogue identities/hashes with the registration/export tools. Upload packets and catalogue together. Reapply/refresh the language to transfer an update; uploading to GitHub does not itself rewrite the stored watch packet.
- A compatible translation edit needs no PBW rebuild if it fits the frozen schema/codebooks/fonts and 2,560-byte cap. New menus/functions, new schema entries, unsupported glyphs or an explicit codec migration may need a build. Small native loading/emergency strings and built-in fallback text also need a build to change.
- Initial watch-language loading and uncached language changes require Internet, Bluetooth and the open watch app. Afterwards the selected language and watch-side lesson management work offline. Phone appointment entry remains optional.
- Largest measured 3.8.55 payload: 2,524 bytes, or 2,540 bytes with persistence metadata. Do not silently increase limits or assume future translations fit. Resource storage, runtime RAM and the older 4,096-byte persistence quota are different budgets; consult docs/memory-comparison-3.8.55.json before making memory claims.

## Verification and durable project notes

- Start resumed work by reading this file, release.json, README.md and the relevant docs. The repository is the durable record; local /tmp files, workspace backups and prior chat context may be unavailable later.
- docs/DEV-3.8.55.md explains LP5, codec reproduction, glyphs, native verification and the Diorite emulator installation workaround. docs/language-pack-support.md records current-only hosting. docs/DEV-3.8.50.md explains compact storage and downgrade recovery. Packs/App/Languages/README.md documents translation registration.
- Relevant checks include projects/<project>/tests/check.py, tests/watch_language_ui_test.py, tests/additional_language_packs_test.py, tests/bridge_snapshot_size_test.py, tests/script_fonts_test.py and tests/script_glyph_coverage_test.py. For a release, run tests/release_validation.py and tools/package_release.py. Run checks appropriate to the actual change; do not repeat full native migrations for documentation-only work.
- Native language/memory testing uses tools/native_generic_memory.py; production phone integration uses tools/live_phone_native_test.js. Preserve the distinction between emulator evidence and physical-watch testing. Keep private native state snapshots and verification captures out of published source archives; docs/verification/dev is ignored.
- Keep store/description-en.md and store/description-de.md aligned with published features. Store descriptions must explain the first language-download requirement and Germany-only training rules. Release notes and SHA-256 downloads belong with each explicitly approved public release.
