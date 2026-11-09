# Languages for Germany

`index.json` maps each exported application version to its manifest. Inside a version folder, `de.json` and `en.json` contain the exact generated phone-side menu packets for Deutsch and English. `manifest.json` records their locale, compatible app version, packet ID, decoded payload size, CRC and SHA-256 of the JSON file.

These are **Germany's training rules with different interface languages**. Other countries will have their own directory under `Packs`.

Regenerate using:

```
python3 tools/export_language_packs.py
```

`tools/sync_release.py` also exports the catalogue after all device projects have been synchronized. The export checks that all five projects use identical packets and the same version. Keep version folders separate: the current decoder and packet IDs are bound to their matching app build. These folders include development versions and do not imply a published GitHub Release.

Starting with development 3.8.44, the phone client downloads the selected version-pinned manifest and packet from this public directory. It checks country, ruleset, version, packet identity, SHA-256 and CRC before forwarding it to the watch. The bundled phone module contains metadata only; full build fixtures are generated in `projects/*/tools/language-packets.json` outside the phone source. The client retains one verified packet in its phone cache. Its current cached language is usable offline; an uncached language requires Internet access. Failed downloads retain the previous cache and watch language. Publish these files before distributing their matching PBW. See [implementation and tests](../../../docs/DEV-3.8.44.md).

Only the selected menu packet is retained on the watch. Longer explanation texts and the small emergency/loading fallback remain bundled in the current prototype.

From 3.8.45 the canonical country directory is `Germany` and new manifests use `rulesetDirectory: Germany`. Archived 3.8.43/3.8.44 manifests retain their original identity. The old `Packs/German` directory has been removed at the owner’s request; use app version 3.8.45 or newer for downloads. From 3.8.46 the settings-language selector and translations are fetched from the settings-v1 catalogue; an English fallback remains bundled.

## Dynamic settings catalogue (3.8.46+)

The index retains `versions` for native menu packets and adds `settings: {format: settings-v1, languages: [...]}`. Each entry has locale, native language name, relative `<locale>/settings.json` path, SHA-256 and watchLanguage (0 for de, 1 for en, null for additional phone-only languages). Settings JSON contains schemaVersion, format, trainingCountry, locale, a flat strings object and the kinds/grounds arrays. See [adding a language without a build](../../../docs/DEV-3.8.46.md#adding-a-language-without-a-build). New custom languages are preserved during export.
