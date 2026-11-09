# Development 3.8.43 — Mutual menu-language swapping

The selected DE or EN menu packet is the only persisted language packet. Changing languages transfers its replacement from the phone. Choosing the current language can reuse its active packet; choosing the other language requires a transfer again. Both phone-side packets remain available without an Internet connection. The watch remains usable offline after the selected packet is installed.

Short German text keys have been replaced in native source by symbolic LK_ identifiers. They resolve through generated language_keys.h and text IDs rather than a compiled German menu dictionary. Readable German originals are retained in tools/language-key-map.json. The same IDs address German or English data. A small bilingual loading notice and emergency reminder controls remain built in. Longer explanation texts remain bundled in both languages, as in the previous prototype; this is a menu-packet swap, not yet a fully externalized text catalogue.

First use after updating requires the phone to install the selected packet, including German. The companion automatically requests a missing selected-language packet when it receives the watch state. While no valid packet is available, a bilingual notice explains how to load one. Normal menu actions wait for that packet; reminder dismissal/snooze controls remain available.

An incoming replacement is staged in temporary RAM while the previous verified packet remains usable. Interrupted or corrupt downloads do not alter the old persisted packet. After verification, its bytes replace the existing data slots and obsolete slots are deleted. A power/storage failure during the short flash commit can require reloading a packet; the loading notice and emergency controls remain available. Only packet keys 9000/9100 onward are written; appointments and training progress keep their existing storage records.

## Memory result versus 3.8.42

See memory-comparison-3.8.43.json for all six native targets. On Time Round, the SDK build's heap reserve grows from **5,040 to 7,460 bytes**, a **2,420-byte increase (48.0%)**. Gains across supported platforms range from 2,296 to 2,563 bytes. The gain comes from removing compiled German menu strings/key tables; transferring bytes alone would not create it.

Persistent package usage is **2,375 bytes for DE** or **2,330 bytes for EN**, including the 16-byte manifest. Compared with 3.8.42's cached English package (2,329 bytes), persistent storage is essentially unchanged; German now also needs a downloaded packet. The older watches' 4KB app-storage quota remains a constraint.

A replacement temporarily allocates its 2,359-byte DE or 2,314-byte EN payload in RAM. In the Time Round home-screen native test, available runtime heap was 3,864 bytes at rest, 1,544 during an EN transfer and 3,864 after cancellation/restart. SDK build reserve and runtime free heap are separate measurements. Read-only decoder resources grow by 1,748 bytes, within the existing 256KB resource budget.

## Validation and maintenance

- C tests cover both full translation sets, repeated DE/EN replacement, idempotent active-packet reuse, interrupted/corrupt downloads, a simulated flash-write failure/recovery and a 4KB quota with 1,500 bytes reserved for application data.
- Phone tests cover DE→EN→DE→EN, acknowledgements while the old language is still active, duplicate acknowledgements, reconnect/restart and initial DE/EN loading.
- Existing model/storage/wakeup checks, unit-entry policy tests and the actual progress-renderer tests retain their previous behavior. Renderer test doubles resolve symbolic keys back to German.
- tools/regression_3843.py exercises native transfer, interruption recovery, offline app restart, menus and replacement storage measurements, while restoring original appointments, progress, topics, remainders, class, profile and language. Development captures and live reports are generated under docs/verification/dev/ and ignored by Git.
- Generated C, key headers, key maps, phone packets, codec resource and fixtures are produced together by tools/sync_release.py. For edits to canonical German text, use generate_language_pack.restore_project first; synchronization restores keys before updating versions and then regenerates them. Do not renumber generated IDs or edit generated data by hand.

No physical-watch testing is claimed. This DEV build is not a GitHub Release. Continue version numbering at 3.8.44.
