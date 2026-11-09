# Current phone and watch languages

Only the current compatibility variant is hosted. Current development app: **3.8.55**; watch format **LP5/shared-bpe-v1**, key **37bc2f9e-869b4728**. The owner explicitly retired the older download variants; see [support policy](../../../docs/language-pack-support.md).

The catalogue `index.json` supplies both the dynamic settings-language list and the current watch-language descriptors. Each of the 24 languages has:

- `<locale>/settings.json`: 86 translated settings strings, seven lesson types and twelve theory topics.
- `<locale>/watch-source.json`: 296 editable watch texts.
- `watch/37bc2f9e-869b4728/<locale>.json`: the compressed watch packet, with identity, CRC and SHA-256 recorded in the catalogue.

| Locale | Language | Watch ID |
| --- | --- | ---: |
| de | Deutsch | 0 |
| en | English | 1 |
| es | Español | 2 |
| fr | Français | 3 |
| it | Italiano | 4 |
| pt | Português | 5 |
| nl | Nederlands | 6 |
| pl | Polski | 7 |
| da | Dansk | 8 |
| sv | Svenska | 9 |
| fi | Suomi | 10 |
| cs | Čeština | 11 |
| hu | Magyar | 12 |
| ro | Română | 13 |
| sk | Slovenčina | 14 |
| hr | Hrvatski | 15 |
| sl | Slovenščina | 16 |
| et | Eesti | 17 |
| lv | Latviešu | 18 |
| lt | Lietuvių | 19 |
| mt | Malti | 20 |
| ga | Gaeilge | 21 |
| el | Ελληνικά | 22 |
| bg | Български | 23 |

## Editing and registration

Compatible text edits and new languages can be published without a PBW build when they fit the existing schema, format placeholders, fonts and 2,560-byte packet cap. Keep internal text keys stable. Never retrain the frozen codec during registration.

For phone settings, translate every key and the kinds/grounds arrays in a copy of the English packet, change its locale, then run:

```
python tools/register_settings_language.py /path/to/settings.json --name "Native language name"
```

DE/EN settings sources are maintained in tools/settings-translations.json. The settings exporter preserves custom locales. Register the phone language before its watch packet:

```
python tools/register_watch_language.py /path/to/watch-source.json
```

For maintained project sources, regenerate all current packets with:

```
python tools/export_language_packs.py
```

Export removes obsolete watch compatibility variants only after all sources encode successfully. It preserves the current variant’s custom registrations. Publish changed packets and the catalogue together.

The seven frozen codebooks share the v7 merge dictionary. The encoder chooses the smallest book for each packet and expands uncoded intermediate tokens into coded children/bytes. The generic decoder has no hard-coded language-ID list. Greek/Cyrillic additionally use the script-font resources bundled in the current PBW. New functions, schemas, unsupported glyphs or codec changes can require a new build.

## Download and storage

The phone verifies the selected packet before transfer. The watch receives it in 128-byte chunks, validates it and retains one selected packet. The chosen language works offline after download; uncached replacements need Internet and a watch connection. Phone settings and watch language can differ until Apply to watch is used.

The current schema retains `trainingCountry: DE`; all 24 translations use Germany’s training rules. Removing historical GitHub files does not change watch RAM or data storage. See [format, packet sizes, fonts and verification](../../../docs/DEV-3.8.55.md). No GitHub Release is created by package/source updates.
