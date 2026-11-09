# Development 3.8.44 — GitHub language downloads

The phone companion now downloads its selected menu packet from `Packs/German/Languages/3.8.44/` on GitHub. `German` identifies Germany's training rules; `de` and `en` identify interface languages. No Austrian or Swiss rules are included.

The bundled phone catalogue contains only versioned metadata and expected hashes, not the two packet payloads. The client validates the version, country, ruleset, format, language, packet ID, size, SHA-256 and CRC before sending a packet to the watch. It uses the exact version directory rather than a moving latest-version pointer.

Only one verified packet is cached on the phone and only one is persisted on the watch. Changing to the other language downloads its replacement. The currently cached language can be reloaded without Internet access, including after the phone companion restarts. The first packet for this app version and a change to an uncached language require Internet access and a connection to the watch. Opening settings retries a previously failed download.

Failed downloads preserve the previous phone cache and watch language. HTTP requests have a 15-second timeout and automatic retries have a 30-second backoff. The settings page distinguishes downloading, watch transfer, offline availability and download errors. A language command remains pending until it succeeds; reopening settings permits an immediate retry.

Native storage and the language decoder are unchanged from 3.8.43. The selected packet occupies 2,375 bytes for German or 2,330 bytes for English, including its manifest. This step removes packet payloads from the phone bundle; it does not create an additional native RAM saving. Longer explanation texts, both read-only decoder tables and the small emergency/loading fallback remain bundled. This is a remote menu-packet implementation, not a fully externalized translation catalogue.

## Verification

All five SDK projects build and combine into a six-platform PBW. C model, persistence, language, wakeup and phone tests pass in all five projects. Remote-client tests cover hash vectors, compatibility checks, damaged packets, timeout/late callbacks, single-cache replacement, offline reuse and preservation of the previous packet after failure.

Live tests use public GitHub HTTPS downloads, the production phone client and actual native AppMessage responses on all six emulators. They exercise DE/EN replacement, offline restart and preservation of appointments, counts, theory topics, extra minutes, class, profile and original language. No application acknowledgements are mocked. Physical-watch testing is still required. Local reports are ignored under `docs/verification/dev/3.8.44/`.

To repeat a live test, install the matching project build in its emulator, then run `node tools/live_phone_native_test.js chalk` (or another platform) with the Pebble SDK environment and network access. The helper requires the local SDK interpreter configured in that script. `node tools/live_remote_language_test.js` tests real HTTP downloads without an emulator.

## Maintenance

`tools/sync_release.py` generates native keys, codecs, phone metadata and full developer fixtures in `projects/*/tools/language-packets.json`, then exports the matching public files and hashes. The full fixtures are outside the bundled phone source. Restore canonical native text using `generate_language_pack.restore_project` before editing generated language keys. Publish the matching version directory before distributing its PBW. Packet metadata pins file contents; changing published packet bytes requires a matching app build.

Source changes are published without a GitHub Release. Test filename: `Fahrschul-Planer-v3.8.44(DEV).pbw`; app version: `3.8.44`. Continue with 3.8.45.
