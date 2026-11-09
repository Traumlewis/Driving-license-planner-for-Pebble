# Development 3.8.53 — Four more EU languages

Finnish (Suomi) and Czech (Čeština), followed by Hungarian (Magyar) and Romanian (Română), join the existing ten phone/watch languages. All four were checked for the required characters and complete packet size before enabling them. Germany's training rules remain in effect in every language.

Install the combined six-platform `Fahrschul-Planer-v3.8.53(DEV).pbw`, open the watch app, reopen phone settings, select the language and use its translated Apply to watch action. The phone fetches compatible translations from GitHub. Only the selected watch language is stored; offline restart uses the saved packet. The initial download and an uncached language switch require Internet access.

## Shared dictionary migration

The owner requested Finnish/Czech and the other two if they fit. Their complete translations exceed the previous frozen v4 codec's packet budget, so this build explicitly extends the shared dictionary. The new frozen file is `tools/watch-codec-v5.json`, with 7,956 BPE tokens. Compatibility tag: `37bc2f9e-afe05be9` (schema 935079838, codec 2950716393). The LP4 format, generic decoder, 2,560-byte payload limit, 16-byte stored metadata and compact appointment/progress records are unchanged. All 296 texts per language remain complete, including legal/help explanations, accents, version placeholders and original credits. No text or character was removed to force a fit.

All older v1/v2/v3/v4 codecs and published compatibility variants remain frozen. Builds before 3.8.53 retain their matching languages and show the new settings translations as phone-only. These four watch languages require the new DEV PBW. Future compatible translations may still be added as data only, but a language is not guaranteed to fit this frozen dictionary. Packets are close to the size limit and every translation change must be re-encoded and validated before publication.

Reproduce the deliberate codec migration into a NEW file:

```
python tools/train_watch_codec.py --output /tmp/reproduced-watch-codec-v5.json --weights tools/watch-codec-v5-weights.json --locales cs,da,de,en,es,fi,fr,hu,it,nl,pl,pt,ro,sv
```

## Fonts

A separate, non-persistent test app (different UUID) drew the required characters using seven built-in Gothic font variants: 14, 14 bold, 18, 18 bold, 24, 24 bold and 28 bold. Czech Čč Ďď Ěě Ňň Řř Šš Ťť Ůů Žž, Hungarian Őő Űű, Romanian Ăă Șș Țț and Finnish Ää Öö Åå were captured on all six native emulator platforms. No custom font resource or layout change is needed. The probe was closed and the original planner reopened. Source is under tools/prototypes/eu_glyph_probe; local screenshots are excluded from source publication.

## Verification and rollback

Verification covers production C decoding of every text in all fourteen languages, an additional language ID created after compilation, transfer corruption/interruption/flash recovery, and the old 4,096-byte persistence quota with 1,500 app-data bytes reserved. Phone/browser checks cover all translated Apply commands, downloads, one cached packet, offline restart, failed replacement preserving the selected language, form preservation and responsive layouts.

Native emulator checks cover all six platforms, language replacement and offline restart, home screenshots and comparison against the pre-upgrade application data. The production phone's real GitHub-to-watch path and old-codec bootstrap are checked separately. These are emulator checks, not physical-watch certification. Local detailed reports remain under docs/verification/dev/3.8.53.

Appointments, class/profile, theory checks, counts, extra minutes and selected language retain the 3.8.52 compact data format. To return to 3.8.52, select a language it supports (DE/EN/ES/FR/IT/PT/NL/PL/DA/SV), install the backed-up PBW over the app, then let the phone download its matching packet. Do not uninstall. A legacy-storage helper is only needed for pre-compact builds, as described in DEV-3.8.50.md.

Backup: /workspace/backups/3.8.52-before-fi-cs-hu-ro contains the prior source/PBW, native snapshots and flash copies. Native version is 3.8.53; DEV occurs only in test filenames. Developer: Traumlewis. Credits: (Idee by Traumlewis | Code by Codex). Source/data and DEV update only; no GitHub Release. Continue at 3.8.54.

## Packet and resource measurements

| Language | Payload | Persisted with metadata |
| --- | ---: | ---: |
| Deutsch | 2,552 B | 2,568 B |
| English | 2,548 B | 2,564 B |
| Español | 2,557 B | 2,573 B |
| Français | 2,532 B | 2,548 B |
| Italiano | 2,467 B | 2,483 B |
| Português | 2,391 B | 2,407 B |
| Nederlands | 2,458 B | 2,474 B |
| Polski | 2,534 B | 2,550 B |
| Dansk | 2,350 B | 2,366 B |
| Svenska | 2,381 B | 2,397 B |
| Suomi | 2,558 B | 2,574 B |
| Čeština | 2,555 B | 2,571 B |
| Magyar | 2,550 B | 2,566 B |
| Română | 2,558 B | 2,574 B |

The largest payload leaves two bytes below the unchanged receiver cap. This does not accumulate fourteen languages on the watch: only one selected packet is stored. The dictionary adds 17,432 resource bytes per platform relative to 3.8.52. SDK application RAM reserves are unchanged on five targets; Time 2 uses four additional bytes of executable/data RAM. The resource and per-app persistence quotas are separate. Actual SDK and native heap measurements are recorded in memory-comparison-3.8.53.json; sampled heap omits transient stack peaks.
