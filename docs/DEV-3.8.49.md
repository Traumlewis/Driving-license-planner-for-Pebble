# Development 3.8.49 — French GitHub language packets

Français is available for the phone settings and the watch. Both translations load from GitHub under Packs/App/Languages. Select Français, then Appliquer à la montre. Germany’s training rules still apply. All 296 watch strings are translated, including the long help/legal explanations; DE/EN/ES remain available. The running version is substituted for {version}, and the owner’s original credits remain unchanged.

## Why this French test needs a PBW update

The complete French translation encoded to 5,287 bytes with 3.8.48’s frozen shared codec, exceeding its 2,560-byte limit. The catalogue alone cannot change that native limit or the bundled decoder resource. This build extends the common codec using the four translation sources and changes the codec compatibility identity. The decoding algorithm, text schema, receive limit, storage keys and native data model remain unchanged. The translations themselves are still remote packets.

The new frozen codec is tools/watch-codec-v2.json (2,841 shared tokens). The previous tools/watch-codec-v1.json and all historical packets remain unchanged. Both variants are published in the live index, so 3.8.48 still downloads its own DE/EN/ES packets and sees French as phone-only. With 3.8.49, the matching catalogue enables French on the watch. No GitHub Release is published.

Compatibility: LP4/shared-bpe-v1, schema 935079838, codec 4102950692, tag 37bc2f9e-f48e0f24. The text schema remains frozen. Additional languages that fit this codec, packet limits and available fonts can still be registered as data without rebuilding. This is not a guarantee that every future language will fit. New codec training is an explicit migration requiring a new build; tools/train_watch_codec.py writes only a new filename and is never invoked by registration or normal builds.

## Memory

Selected watch packets persist one at a time, with 16 bytes of metadata:

| Language | Payload | Persisted |
| --- | ---: | ---: |
| Deutsch | 2,538 B | 2,554 B |
| English | 2,280 B | 2,296 B |
| Español | 2,551 B | 2,567 B |
| Français | 2,407 B | 2,423 B |

Payload limit remains 2,560 bytes. The shared codec resource grows by 4,896 bytes; Time Round total resources are 32,197 of 262,144 bytes. This is a resource-storage tradeoff, not an overall flash saving. Time Round SDK free heap is 9,050 bytes versus 9,042 in 3.8.48. Other targets retain their prior native RAM reserve or gain eight bytes. The resource-page cache and temporary packet staging are unchanged.

Final French transfer samples: Time Round 5,456 bytes free at rest, 3,044 during download and 5,456 afterwards; Core 2 Duo 8,464 / 6,052 / 8,464 bytes.

See memory-comparison-3.8.49.json for all SDK results and native transfer measurements. Runtime samples do not include maximum transient stack usage.

## Validation

C tests decode all DE/EN/ES/FR strings plus a data-only language 17, verify restart/integrity/format signatures, corrupt/interrupted downloads and flash-commit recovery, and enforce the older watches’ 4KB app quota with 1,500 bytes reserved for app records. Phone tests cover French download/transfer/bootstrap, one cached packet, offline reuse and validation. Browser tests exercise the actual French settings and its language-3 Apply command. Older firmware can spend around 9–12 seconds validating the last chunk. The phone now allows 30 seconds for this final acknowledgement, retaining 7 seconds for normal chunks, to avoid redundant retransfers.

Native tests use actual GitHub HTTPS downloads and real AppMessage acknowledgements; snapshots before/after installation check app-data preservation. Physical-watch testing remains the purpose of this DEV PBW.

Backup: /workspace/backups/3.8.48-before-french/source.zip. Combined six-platform test PBW: Fahrschul-Planer-v3.8.49(DEV).pbw. Native version has no DEV suffix. Continue at 3.8.50.
