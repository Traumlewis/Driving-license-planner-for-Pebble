# Development 3.8.48 — Universal watch language packets

The watch now accepts compatible self-describing LP4 packets instead of a compiled DE/EN packet table. German, English and Spanish, including long explanations, load from GitHub through the phone companion. Spanish's **Aplicar al reloj** button is enabled in this build. Appointments, manual counters, topic checkmarks, remainders, class/profile and original settings retain their storage keys.

Install this PBW once. Future compatible translations can then be added as data without building again. The existing system fonts must support their characters and the packet must fit the decoder's limits. German driving-training rules still apply in every language.

## Data and compatibility

`Packs/App/Languages/index.json` retains its settings-v1 list and adds watchPacks variants keyed by the native text-schema ID and shared-codec ID. Under `watch/<schema>-<codec>/` each locale has its packed JSON. Editable translations live at `<locale>/watch-source.json`. All 296 translated text keys, including help/legal explanations, are covered. Native keys and version placeholders are language independent; `{version}` is replaced by the running app version on the watch.

The compiled receiver contains the schema/codec identities and limits, not a fixed language list or expected language-packet IDs. Language numbers 0–63 are accepted when the received packet validates; 0/1 remain German/English. The phone resolves the locale and packet identity from the live catalogue. Existing 3.8.47 companions ignore the watchPacks extension and continue treating Spanish as phone-only. They need the one-time 3.8.48 update for watch Spanish.

The phone validates catalogue country/format/paths, schema and codec, packet identity/size, SHA-256, header and CRC. The watch checks its header, checksums, bounded directory and text decoding, UTF-8, per-key length and formatting signatures before committing. Incoming bytes remain in temporary RAM until validation completes. Interrupted/corrupt downloads leave the previous packet intact. A flash-write/power failure during commit may require reloading the packet; emergency controls remain available and application-data keys are not rewritten.

Only one watch packet and one separate settings packet are cached on the phone; one watch packet is persisted on the watch. Catalogue metadata and a shared read-only compression codebook are also retained. A small emergency/loading fallback remains built in. The shared codebook contains reusable fragments learned from the initial translation corpus; it is not regenerated when another language is registered. There are no separately compiled per-language decoder tables or long-text dictionaries.

## Add another language without a build

1. Register its translated settings.json with `tools/register_settings_language.py` as before.
2. Copy `Packs/App/Languages/en/watch-source.json`. Change locale, name (at most 23 UTF-8 bytes), and a free language number 2–63. Translate every value under strings, retaining the German reference keys, format specifiers and `{version}` tokens.
3. Run `python3 tools/register_watch_language.py /path/to/watch-source.json`. It uses the frozen schema/codec, validates completeness and format signatures, enforces the 2,560-byte packet limit and updates the matching watchPacks catalogue.
4. Publish the source, packed packet and index together. Reopen settings, select the language, then apply it to the watch.

For updates to an existing language retain its number. The codec and key schema in tools are frozen compatibility inputs. A new app feature/text schema, unsupported glyphs or a packet that cannot be shortened to fit can require another build. Adding a translation does not itself run a build or publish a GitHub Release.

## Memory

See [the SDK comparison](memory-comparison-3.8.48.json) for every platform. Values distinguish SDK heap reserve, runtime free heap, persistent packet bytes and resource storage. No overall flash saving is claimed: the shared codebook grows the resource bundle while removing compiled text and per-language decoding metadata saves application RAM.

On Time Round, SDK free heap rises from 7,452 to 9,042 bytes (+1,590). In the native home-screen test, runtime free heap is 5,448 bytes at rest, 2,924 while receiving Spanish and 5,448 afterwards. Core 2 Duo measures 8,456 / 5,932 / 8,456 bytes. These transfer samples exclude transient call-stack usage and are not a claim of absolute peak free memory.

Persisted packet sizes (including the 16-byte manifest): German 2,528 bytes, English 2,319 bytes, Spanish 2,536 bytes. The receiver permits at most 2,560 payload bytes plus 16 manifest bytes. C quota tests reserve 1,500 of the older watches' 4,096 app-storage bytes for application records.

Incoming transfer RAM is approximately the payload size plus allocator bookkeeping. Decoding uses bounded shared buffers and a 512-byte resource-page cache. Format/length metadata is read from resources. Startup checks persisted integrity and its directory; complete text validation runs only on new packets. The decoder is iterative and reuses small buffers, keeping large temporary arrays out of the app's persistent main stack frame. Early prototypes exceeded the older firmware stack guard; these were corrected before distribution.

## Verification

C tests cover all DE/EN/ES texts and an additional data-only language number 17, restart, corrupt/interrupted transfers, flash-commit failure/recovery and the 4KB quota. Phone tests cover dynamic metadata, schema/codec/path/hash checks, one cached packet, offline reuse, unknown data-only languages, pending transfer/reconnect and supported-language selection. Existing model/storage/reminder, progress-renderer, optional-units and circular-scrolling regressions pass.

Browser tests verify that Spanish is no longer phone-only, its Apply to watch button sends language 2, and existing settings behavior/form preservation/layouts remain intact. Live HTTPS tests exercise the production download client against GitHub. Native emulator tests exercise real application acknowledgements, DE/EN/ES replacement, offline restart and data preservation. A separate native test creates language 17 only after the binary is built and verifies it without changing that binary. Local reports/screenshots are ignored under docs/verification/dev/3.8.48/. Physical-watch testing is still required.

Combined six-platform test PBW; version 3.8.48, developer Traumlewis. DEV is only in the filename. Source/data updates only; no GitHub Release. Continue at 3.8.49.
