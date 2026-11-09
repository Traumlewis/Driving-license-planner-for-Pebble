# Phone settings languages

`index.json` lists settings-v1 translations for the phone settings page. Each language has its own `<locale>/settings.json`, such as `de/settings.json`, `en/settings.json` and `es/settings.json`.

New compatible translations can be added without rebuilding the PBW: translate all keys and the kinds/grounds arrays in a copy of the English packet, change its locale, then run:

```
python3 tools/register_settings_language.py /path/to/settings.json --name "Français"
```

Publish the resulting packet and index together. The helper validates the data, calculates SHA-256 and marks additional languages as phone-only. DE/EN source translations are maintained in `tools/settings-translations.json` and exported by `tools/export_settings_languages.py`. Exports preserve custom languages.

The settings-v1 schema retains its trainingCountry DE compatibility field. Current LP4 watch packets live under `watch/<schema>-<codec>/`; `Packs/Germany/Languages` retains historical LP3 packets. The phone retains one selected settings packet and an English emergency fallback remains bundled.

See [directory migration](../../../docs/DEV-3.8.47.md) and [format and behavior](../../../docs/DEV-3.8.46.md). Use 3.8.47 or newer for this download path. Repository updates do not publish a GitHub Release.

Available settings languages: Deutsch, English, Español and Français. Spanish/French are phone-only on 3.8.47; watch support depends on the compatible LP4 catalogue. Germany’s training rules remain unchanged.

## Watch packets (3.8.48+)

DE/EN/ES also have watch-source.json translations and packed LP4 data under watch/<schema>-<codec>/. The live index maps compatible builds to their watch languages. Use tools/register_watch_language.py to add another complete watch translation without rebuilding; see [the guide and memory limits](../../../docs/DEV-3.8.48.md). Spanish is phone-only on 3.8.47, and available on the watch after installing 3.8.48. Keep legacy settings watchLanguage fields unchanged; watchPacks supplies the generic receiver mapping.

## French (3.8.49+)

French settings: `fr/settings.json`; all 296 watch translations: `fr/watch-source.json`. French is watch language 3. The expanded frozen v2 codec uses compatibility tag `37bc2f9e-f48e0f24`; French requires the 3.8.49 DEV PBW. Its payload is 2,407 bytes, within the unchanged 2,560-byte limit. The previous codec variant remains published for 3.8.48. Translations still download from GitHub; do not train a codec during normal language registration. See [French testing and memory](../../../docs/DEV-3.8.49.md).
