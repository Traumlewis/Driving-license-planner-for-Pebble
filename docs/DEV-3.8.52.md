# Development 3.8.52 — Danish and Swedish watch languages

Dansk and Svenska join Deutsch, English, Español, Français, Italiano, Português, Nederlands and Polski on the phone and watch. Install the combined six-platform `Fahrschul-Planer-v3.8.52(DEV).pbw`, open the watch app, reopen phone settings, select the language and use its translated Apply to watch action. An uncached language needs Internet; the selected watch packet remains available after an offline restart.

The owner explicitly requested another shared-dictionary extension after complete Danish and Swedish drafts exceeded the 3.8.51 codec's limit. The translations still download from GitHub. Only the selected language is stored on the watch. Germany's training rules remain in effect for every language.

## Frozen codec migration

The new frozen codec is `tools/watch-codec-v4.json`, with 5,777 BPE tokens. Compatibility tag: `37bc2f9e-ba59526d` (schema 935079838, codec 3126415981). All ten sources contain the same complete 296-text schema, including statuses, theory topics and long legal/help explanations. No texts or accents were removed to force a fit. The LP4 format, generic decoder, 2,560-byte payload limit, 16-byte metadata and compact application-data format are unchanged.

Previous v1/v2/v3 codecs and all their published packet variants remain frozen. Older PBWs continue receiving their matching packets; Danish and Swedish watch support requires this DEV build. The former da/sv watch-draft.json files are replaced with watch-source.json, plus complete 86-string settings packets. No GitHub Release is published.

The shared Huffman book was explicitly balanced with recorded locale weights. All byte values retain fallback codes. Reproduce into a NEW filename:

```
python tools/train_watch_codec.py --output /tmp/reproduced-watch-codec-v4.json --limit 8192 --frequency-scale 1024 --weights tools/watch-codec-v4-weights.json --locales da,de,en,es,fr,it,nl,pl,pt,sv
```

The result is compared byte for byte with the frozen v4 file. The locale selector also makes prior codec recipes reproducible after further sources are added. Normal registration/builds never retrain a dictionary. Future translations still need to fit the frozen codec/schema/glyph/size requirements; support without another build is not guaranteed.

## Packet sizes

| Language | Payload | Persisted with metadata |
| --- | ---: | ---: |
| Deutsch | 2,474 B | 2,490 B |
| English | 2,389 B | 2,405 B |
| Español | 2,490 B | 2,506 B |
| Français | 2,466 B | 2,482 B |
| Italiano | 2,308 B | 2,324 B |
| Português | 2,203 B | 2,219 B |
| Nederlands | 2,280 B | 2,296 B |
| Polski | 2,487 B | 2,503 B |
| Dansk | 2,177 B | 2,193 B |
| Svenska | 2,205 B | 2,221 B |

The dictionary resource grows by 7,424 bytes relative to 3.8.51. SDK application RAM reserves are unchanged on all six targets. See `memory-comparison-3.8.52.json` for SDK reserves and native transfer samples; these heap samples omit transient stack peaks. Resource storage is separate from the selected packet's per-app persistence quota. C tests reserve 1,500 bytes for application data while enforcing the older 4,096-byte quota.

## Validation and rollback

Validation includes all 296 texts in ten languages plus a new language ID created after compilation, corruption/interruption/flash recovery, all ten phone Apply commands, one-cache/offline behavior, preserved form input and responsive phone layouts. Native emulator tests exercise all six platforms, language replacement and offline restart, memory samples, home screenshots and comparison against pre-upgrade application data. The actual production phone client's GitHub download/native transfer path and old-codec bootstrap are tested separately. These are emulator tests, not physical-watch certification.

Appointments, counters, theory checks, class/profile, extra minutes and selected language are preserved. Compact records remain compatible with 3.8.51. To return, choose a language supported by 3.8.51 (DE/EN/ES/FR/IT/PT/NL/PL), install the backed-up PBW over the existing app, then let the phone fetch its matching packet. Do not uninstall. Returning to pre-compact app versions still requires the separate legacy-storage helper documented in DEV-3.8.50.md.

The prior source/PBW, native snapshots and emulator flash copies are backed up at `/workspace/backups/3.8.51-before-da-sv`. Local native reports/screenshots under `docs/verification/dev/3.8.52` are excluded from source publication. Native version is 3.8.52; DEV is only in test filenames. Developer: Traumlewis. Credits: (Idee by Traumlewis | Code by Codex). Continue at 3.8.53.
