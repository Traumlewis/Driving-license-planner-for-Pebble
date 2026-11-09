# Development 3.8.51 — Eight remote watch languages

Italiano, Português (European Portuguese), Nederlands and Polski are available on the watch alongside Deutsch, English, Español and Français. Install the combined six-platform `Fahrschul-Planer-v3.8.51(DEV).pbw`, open the watch app, reopen phone settings, select the language and use the translated Apply to watch button. Internet is required to fetch an uncached language; the selected watch packet remains available after an offline restart.

Appointments, class/profile, counters, theory checkmarks and extra minutes retain the 3.8.50 compact storage format and keys. No uninstall or data reset is required. Germany's training rules remain in effect in every language. Native version is 3.8.51; DEV appears only in test filenames. Developer: Traumlewis. Credits: (Idee by Traumlewis | Code by Codex).

## Explicit shared-codec migration

The owner selected Option 1: extend the dictionary bundled with the PBW while keeping translations downloaded from GitHub. All 296 strings per language, including help/legal explanations, remain complete. No language text was removed to meet the packet limit. The LP4 wire format, receiver algorithm, 2,560-byte payload limit, 16-byte persisted metadata and one-active-packet policy are unchanged.

The new frozen codec is `tools/watch-codec-v3.json`, with 4,849 BPE tokens. Compatibility is `37bc2f9e-0148b906` (schema 935079838, codec 21543174). Existing v1/v2 codec files and published packet variants are preserved. Older PBWs continue seeing their matching languages; the four new watch languages require 3.8.51. The former watch-draft.json files have become watch-source.json translations.

The Huffman trainer balances the largest packets using explicit locale weights and gives unused fallback tokens a low nonzero weight. All 256 byte values remain encodable; compatible future languages can still be registered as data if they fit the frozen codec, text schema, supported glyphs and packet size. A future language is not guaranteed to fit. Normal registration/builds never retrain the dictionary.

Reproduce this deliberate migration into a NEW file:

```
python tools/train_watch_codec.py --output /tmp/reproduced-watch-codec-v3.json --limit 8192 --frequency-scale 1024 --weights tools/watch-codec-v3-weights.json
```

The generated file was compared byte for byte with the frozen v3 codec.

## Memory

| Language | Payload | Persisted with metadata |
| --- | ---: | ---: |
| Deutsch | 2,489 B | 2,505 B |
| English | 2,395 B | 2,411 B |
| Español | 2,476 B | 2,492 B |
| Français | 2,465 B | 2,481 B |
| Italiano | 2,270 B | 2,286 B |
| Português | 2,169 B | 2,185 B |
| Nederlands | 2,269 B | 2,285 B |
| Polski | 2,444 B | 2,460 B |

The shared resource grows by 16,064 bytes on every platform. SDK RAM reserves and free application heap are unchanged from 3.8.50 on all six targets. Total resources range from 47,793 to 49,792 bytes; the round Time Round uses 48,261 of its 262,144-byte resource budget. Only the selected packet is saved in the app's persistence quota, so adding catalogue entries does not accumulate languages on the watch. The maximum selected packet plus metadata is now 2,505 bytes. C tests enforce the older 4,096-byte app quota with 1,500 bytes reserved for app data.

See `memory-comparison-3.8.51.json` for SDK and native transfer samples. Samples do not include transient stack peaks. Resource storage and the per-app data quota are separate budgets.

## Verification and rollback

Verification covers production C decoding of all 296 strings in all eight languages, an additional language number created after compilation, corruption/interruption/restart/flash-commit recovery, and protected app-data behavior. Phone tests cover IDs 0–7, cold bootstrap, transfer ACKs and one-packet/offline caching. Chromium checks all eight translated Apply actions; the four new phone translations retain form data across language changes and survive offline reload/failure recovery.

Native emulator checks cover all six platforms, eight language replacements and offline restarts, comparison with pre-upgrade application data, memory samples and home screenshots. The production phone client's actual GitHub download/transfer path is checked separately. These are emulator checks, not a claim of physical-watch testing. Detailed local screenshots/reports under `docs/verification/dev/3.8.51` are excluded from public source.

For return to 3.8.50, first select an old-build-supported language (DE/EN/ES/FR), install the backed-up PBW over the existing app, then let the phone fetch that build's matching packet. Compact app records remain readable by 3.8.50; a legacy-restore helper is only needed when returning to the older raw-record storage described in DEV-3.8.50.md. Do not uninstall.

Backup: `/workspace/backups/3.8.50-before-eight-languages` contains the previous PBW/source, native state snapshots and emulator flash copies. Source/data updates only; no GitHub Release. Continue at 3.8.52.
