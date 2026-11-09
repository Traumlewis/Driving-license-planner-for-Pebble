# Development 3.8.54 — Slovak, Croatian, Slovenian and Estonian

Slovenčina (Slovak), Hrvatski (Croatian), Slovenščina (Slovenian) and Eesti (Estonian) join the previous fourteen phone/watch languages. All four have complete 296-text watch translations and 86-string phone settings, including lesson types, theory topics, explanations, statuses and error messages. Germany's training rules remain in effect in every language.

Install the combined six-platform `Fahrschul-Planer-v3.8.54(DEV).pbw`, open the watch app, reopen phone settings, select a language and use its translated Apply to watch action. The selected translations are fetched from GitHub. Only the selected packet is stored on the watch; offline restart uses it without another download. Uncached changes need Internet access.

## Explicit codec migration

The current owner requested testing these four languages and a new DEV build if they fit. The previous frozen v5 codec produced 4,738 / 4,787 / 4,630 / 4,862-byte packets, exceeding the unchanged 2,560-byte limit. This build deliberately extends and freezes the shared v6 dictionary rather than removing texts or accents.

The new file is tools/watch-codec-v6.json, with 9,915 BPE tokens. Compatibility tag: `37bc2f9e-e4846e13` (schema 935079838, codec 3833884179). The generic LP4 receiver, schema, packet cap, 16-byte persistence metadata and compact app-data format are unchanged. All previous v1–v5 codecs and their published packet variants remain frozen. Older builds continue using their matching variants and show the four new phone translations as phone-only.

The training tool now allows up to 16,384 merge tokens for an explicit migration. The default remains 8,192; no build or registration retrains a codec. The native signed 16-bit tree representation still accommodates that training ceiling. This migration actually uses 9,915 tokens, retaining the same bounded resource cache and one selected language. Reproduce into a NEW file:

```
python tools/train_watch_codec.py --output /tmp/reproduced-watch-codec-v6.json --limit 16384 --weights tools/watch-codec-v6-weights.json --locales cs,da,de,en,es,et,fi,fr,hr,hu,it,nl,pl,pt,ro,sk,sl,sv
```

Future translations still have to fit the frozen codec/schema/size/glyph requirements; adding another language without rebuilding is not guaranteed.

## Packet sizes

| Language | Payload | Persisted with metadata |
| --- | ---: | ---: |
| Deutsch | 2,540 B | 2,556 B |
| English | 2,517 B | 2,533 B |
| Español | 2,538 B | 2,554 B |
| Français | 2,542 B | 2,558 B |
| Italiano | 2,500 B | 2,516 B |
| Português | 2,419 B | 2,435 B |
| Nederlands | 2,551 B | 2,567 B |
| Polski | 2,551 B | 2,567 B |
| Dansk | 2,437 B | 2,453 B |
| Svenska | 2,470 B | 2,486 B |
| Suomi | 2,545 B | 2,561 B |
| Čeština | 2,450 B | 2,466 B |
| Magyar | 2,552 B | 2,568 B |
| Română | 2,519 B | 2,535 B |
| Slovenčina | 2,492 B | 2,508 B |
| Hrvatski | 2,536 B | 2,552 B |
| Slovenščina | 2,548 B | 2,564 B |
| Eesti | 2,542 B | 2,558 B |

The maximum payload leaves eight bytes below the cap. Every translation edit must therefore be re-encoded and validated. The dictionary resource grows by 15,672 bytes per platform relative to 3.8.53. SDK application RAM usage grows by eight bytes on Time 2 and sixteen bytes on the other five targets. Resource storage and the selected packet's per-app data quota are separate budgets. Actual SDK reserves and native memory samples are recorded in memory-comparison-3.8.54.json; heap samples omit transient stack peaks.

## Fonts and compatibility

A separate, non-persistent test app with its own UUID drew the required characters in seven existing system Gothic variants (14, 14 bold, 18, 18 bold, 24, 24 bold, 28 bold) on all six native emulator platforms. The new samples cover Ĺĺ Ľľ Ŕŕ Čč Ćć Đđ Šš Žž Ôô and Õõ Ää Öö Üü Ďď Ťť Ňň. All required characters render; no custom font or layout changes are needed. The original planner was reopened afterwards. Probe source is under tools/prototypes/eu_glyph_probe; 84 local screenshots are under docs/verification/dev/eu-glyph-probe-18 and excluded from publication.

Real language IDs now cover 0–17, with Estonian using 17. The data-only post-build verification language therefore uses test ID 42 rather than the former test-only 17. This changes lab fixtures only, not the generic native protocol. Unsupported ID 63 remains a negative phone-command case.

The complete compatibility catalogue has grown. Lab HTTPS adapters allow the same 60KB response budget as the existing production downloader instead of their former artificial 20KB download cap; the production packet validator still enforces its separate 20KB JSON and 2,560-byte decoded packet limits. No production download limit or older-build behavior is changed.

## Verification and rollback

Checks cover decoding all 296 texts in eighteen languages plus data-only ID 42, corruption/interrupted transfer/flash recovery, older 4,096-byte persistence quota with 1,500 application-data bytes reserved, all translated phone Apply commands, form preservation and one-cache offline behavior. Native emulator tests cover all six platforms, eighteen language replacements, offline restart, screenshots, memory samples and comparison with pre-upgrade application data. Actual production phone downloads from GitHub and old-codec bootstrap/return are tested separately. These are emulator tests, not a claim of physical-watch certification.

Appointments, class/profile, theory checks, counts, extra minutes and selected language retain the compact data format. To return to 3.8.53, choose one of its fourteen languages, install the backed-up PBW over the existing app, then let the phone fetch that build's matching packet. Do not uninstall. Pre-compact builds still require the legacy-storage helper described in DEV-3.8.50.md.

Backup: /workspace/backups/3.8.53-before-sk-hr-sl-et includes the prior source/PBW, native snapshots and flash copies. Detailed verification reports stay locally under docs/verification/dev/3.8.54. Native version is 3.8.54; DEV is only in test filenames. Developer: Traumlewis. Credits: (Idee by Traumlewis | Code by Codex). Source/data and DEV update only; no GitHub Release. Continue at 3.8.55.
