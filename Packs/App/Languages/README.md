# Phone settings languages

`index.json` lists settings-v1 translations for the phone settings page. Each language has its own `<locale>/settings.json`, such as `de/settings.json` and `en/settings.json`.

New compatible translations can be added without rebuilding the PBW: translate all keys and the kinds/grounds arrays in a copy of the English packet, change its locale, then run:

```
python3 tools/register_settings_language.py /path/to/settings.json --name "Français"
```

Publish the resulting packet and index together. The helper validates the data, calculates SHA-256 and marks additional languages as phone-only. DE/EN source translations are maintained in `tools/settings-translations.json` and exported by `tools/export_settings_languages.py`. Exports preserve custom languages.

The existing settings-v1 schema retains its trainingCountry DE compatibility field. The watch's versioned menu-language packets are separate under `Packs/Germany/Languages`; additional watch-language decoding and glyph support remain deferred. The phone retains one selected settings packet and an English emergency fallback remains bundled.

See [directory migration](../../../docs/DEV-3.8.47.md) and [format and behavior](../../../docs/DEV-3.8.46.md). Use 3.8.47 or newer for this download path. Repository updates do not publish a GitHub Release.
