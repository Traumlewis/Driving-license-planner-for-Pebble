# Development 3.8.55 — all 24 official EU interface languages

Latviešu (Latvian, ID 18), Lietuvių (Lithuanian, 19), Malti (Maltese, 20), Gaeilge (Irish, 21), Ελληνικά (Greek, 22) and Български (Bulgarian, 23) join the previous eighteen phone/watch languages. Each has 296 watch texts, 86 phone strings, seven lesson types and twelve theory topics. Germany remains the training jurisdiction; translations do not introduce other countries’ licensing rules.

Install the combined six-platform `Fahrschul-Planer-v3.8.55(DEV).pbw`, open the watch app, reopen phone settings, select a language and apply it to the watch. GitHub supplies the selected translation; only one selected watch packet and one phone packet are cached. After the first successful download, the chosen language survives offline restart. Initial installation and uncached replacements need Internet and a watch connection. No GitHub Release is published.

## Explicit LP5 migration

The old v6 dictionary cannot fit the new translations: LV/LT/MT/GA need 8,548 / 6,271 / 7,592 / 6,576 bytes, and the first EL/BG trials need about 41.9/40.0KB against the unchanged 2,560-byte cap. A single newly trained codebook still leaves a 2,769-byte worst case. This build therefore deliberately introduces **LP5/shared-bpe-v1**: a frozen shared BPE dictionary and seven frozen prefix-code books, selected by each packet’s contents rather than a compiled list of language IDs.

The resource has 13,871 merge entries, 15,278 prefix-tree nodes and seven roots. Packet encoding chooses the smallest of the seven books. Every book includes all 256 byte fallbacks; an intermediate merge absent from a book expands into coded children. New compatible translations therefore remain data-only. No translation registration retrains or changes this resource.

The 24-byte packet header, body length directory, 128-byte chunks, 2,560-byte cap, 16-byte persistence metadata and compact application-data format are unchanged. Header bytes 0–2 are `LP5`; byte 3 selects book 0–6. The resource adds a bounded root directory before text limits/signatures. Native validation rejects unsupported books before staging. Schema stays 935079838; codec becomes **2258323240**, compatibility **37bc2f9e-869b4728**. All seven codebooks are exercised by actual language fixtures. Late test ID 42 also changes a translated text after the build.

All v1–v6 dictionaries, previous schema and published older variants stay immutable. Older builds continue to download their own compatible LP3/LP4 variant; the six new phone languages show as phone-only there. A one-time new PBW is necessary for this format/font migration. Further texts must still fit the frozen schema, codebooks, size and glyph coverage.

Reproduce the v7 book into a new file:

```
python tools/train_watch_codec.py --output /tmp/reproduced-watch-codec-v7.json --limit 16384 --weights tools/watch-codec-v7-weights.json --groups tools/watch-codec-v7-groups.json --locales bg,cs,da,de,el,en,es,et,fi,fr,ga,hr,hu,it,lt,lv,mt,nl,pl,pt,ro,sk,sl,sv
```

The canonical trainer reproduces the frozen file byte-for-byte. The ordinary encoder now indexes strings by adjacent token pairs instead of rescanning every string for every merge. Its merge output was compared with an independent reference for all 24 corpora; the native decoder separately verifies every text against its uncompressed source. This affects generation time, not the on-watch memory model.

## Fonts and original design

The system-font probe renders the Latin additions for Latvian, Lithuanian, Maltese and Irish. Greek/Cyrillic produce missing-glyph boxes in the existing Gothic fonts. Seven resource-backed Open Sans Condensed variants provide those scripts at the existing Gothic sizes/weights. Latin languages keep their original system fonts, and numeric Bitham fonts remain unchanged. Layouts, colours, icons and navigation are retained.

A Greek/Cyrillic autonym in the selected packet name chooses the extended fonts without hard-coded language IDs. Descriptors load lazily and remain valid until app exit; TextLayer retains font pointers, so swaps must not unload them prematurely. Seven descriptors used 420 heap bytes in the isolated native probe. Font source and full Apache 2.0 attribution/license are under each project’s resources/fonts. All 180 characters used in the Greek/Bulgarian watch texts are present in all seven source-font variants and included in the generated ranges.

The independent probe app uses UUID 75cf6ad1-71f5-449c-9b0e-e1a055126adf and never writes planner records. System and custom campaigns have separate local screenshots under docs/verification/dev/eu-glyph-probe-24 and eu-glyph-probe-24-custom. Probe source is tools/prototypes/eu_glyph_probe. Native UI screenshots and transfer reports stay under docs/verification/dev/3.8.55 and are excluded from publication.

## Memory

Resource growth relative to 3.8.54 is **88,781 bytes per target**: 36,284 bytes for the codec change and 52,497 bytes for fonts. Total resources are 177,102–179,101 bytes, below the SDK 256KB resource limit. SDK RAM grows by 272–372 bytes depending on the target; Time Round retains 7,320 bytes of SDK heap before runtime allocations. Loaded script-font descriptors add at most 420 bytes dynamically. Heap snapshots exclude transient stack peaks.

| Language | Payload B | Stored with metadata B |
| --- | ---: | ---: |
| Deutsch | 2444 | 2460 |
| English | 2278 | 2294 |
| Español | 2334 | 2350 |
| Français | 2375 | 2391 |
| Italiano | 2153 | 2169 |
| Português | 2082 | 2098 |
| Nederlands | 2156 | 2172 |
| Polski | 2320 | 2336 |
| Dansk | 2035 | 2051 |
| Svenska | 2060 | 2076 |
| Suomi | 2388 | 2404 |
| Čeština | 1990 | 2006 |
| Magyar | 2402 | 2418 |
| Română | 2305 | 2321 |
| Slovenčina | 2010 | 2026 |
| Hrvatski | 2155 | 2171 |
| Slovenščina | 2113 | 2129 |
| Eesti | 2287 | 2303 |
| Latviešu | 2454 | 2470 |
| Lietuvių | 2524 | 2540 |
| Malti | 2514 | 2530 |
| Gaeilge | 2521 | 2537 |
| Ελληνικά | 2240 | 2256 |
| Български | 2273 | 2289 |

The largest packet leaves 36 bytes below the cap. With metadata it uses 2,540 bytes, leaving 1,556 bytes of an older 4,096-byte app-data quota. Unit tests reserve 1,500 bytes for unrelated application records. Full regular appointments continue using the existing compact store. Exact SDK deltas and actual native samples are in memory-comparison-3.8.55.json.

## Verification and data preservation

Checks cover all 24 complete translations and post-build data-only ID 42, bounded font selection/caching and retained-pointer lifetime, all shipped script characters, every codebook and invalid book rejection, corruption/interruption/flash recovery, automatic phone refresh, translated Apply commands, responsive phone layouts, form preservation, one-cache offline reuse and failed replacement. Sanitizer checks cover decoder bounds/undefined behaviour; leak-sanitizer ptrace is unavailable in this sandbox.

The Diorite emulator’s normal PyPKJS installation transport repeatedly failed and once displayed firmware error fe504503. A CPU-only restart retained the same flash; the control 3.8.54 reinstall succeeded. Stopping that emulator’s phone simulator and installing the unchanged combined PBW directly over QEMU with a 10ms packet throttle succeeded. This is an emulator transport limitation, not proof of a physical-watch installation issue. No app uninstall or persistent-flash erase was used; before/after data are checked separately.

Native tests cover the six supported emulator targets, language swaps, offline restart, UI screenshots and memory sampling. Production phone integration downloads the actual GitHub catalogue/settings/packets before transferring them to the native watch app. Pre-upgrade appointments, checkboxes, counters, remainders, selected class/profile and language are compared after testing. These are emulator checks, not physical-watch certification.

Backup: /workspace/backups/3.8.54-before-eu-final-six contains the previous source/PBW, native snapshots and flash copies. Returning to 3.8.54 requires choosing one of its eighteen supported languages, installing the backed-up PBW over the existing app and fetching its matching LP4 packet. Do not uninstall. Pre-3.8.50 builds still require the legacy-storage helper; compact app records themselves are unchanged here.

Native version is 3.8.55; DEV appears only in test filenames. Developer Traumlewis; credits (Idee by Traumlewis | Code by Codex). Continue at 3.8.56.
