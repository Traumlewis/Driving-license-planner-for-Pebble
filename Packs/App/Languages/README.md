# Phone settings languages

`index.json` lists settings-v1 translations for the phone settings page. Each language has its own `<locale>/settings.json`, such as `de/settings.json`, `en/settings.json` and `es/settings.json`.

New compatible translations can be added without rebuilding the PBW: translate all keys and the kinds/grounds arrays in a copy of the English packet, change its locale, then run:

```
python3 tools/register_settings_language.py /path/to/settings.json --name "Français"
```

Publish the resulting packet and index together. The helper validates the data, calculates SHA-256 and marks additional languages as phone-only. DE/EN source translations are maintained in `tools/settings-translations.json` and exported by `tools/export_settings_languages.py`. Exports preserve custom languages.

The settings-v1 schema retains its trainingCountry DE compatibility field. Current LP4 watch packets live under `watch/<schema>-<codec>/`; `Packs/Germany/Languages` retains historical LP3 packets. The phone retains one selected settings packet and an English emergency fallback remains bundled.

See [directory migration](../../../docs/DEV-3.8.47.md) and [format and behavior](../../../docs/DEV-3.8.46.md). Use 3.8.47 or newer for this download path. Repository updates do not publish a GitHub Release.

Available settings languages: Deutsch, English, Español, Français, Italiano, Português, Nederlands, Polski, Dansk, Svenska, Suomi, Čeština, Magyar, Română, Slovenčina, Hrvatski, Slovenščina and Eesti. Spanish/French are phone-only on 3.8.47; watch support depends on the compatible LP4 catalogue. Germany’s training rules remain unchanged.

## Watch packets (3.8.48+)

DE/EN/ES also have watch-source.json translations and packed LP4 data under watch/<schema>-<codec>/. The live index maps compatible builds to their watch languages. Use tools/register_watch_language.py to add another complete watch translation without rebuilding; see [the guide and memory limits](../../../docs/DEV-3.8.48.md). Spanish is phone-only on 3.8.47, and available on the watch after installing 3.8.48. Keep legacy settings watchLanguage fields unchanged; watchPacks supplies the generic receiver mapping.

## French (3.8.49+)

French settings: `fr/settings.json`; all 296 watch translations: `fr/watch-source.json`. French is watch language 3. The expanded frozen v2 codec uses compatibility tag `37bc2f9e-f48e0f24`; French requires the 3.8.49 DEV PBW. Its payload is 2,407 bytes, within the unchanged 2,560-byte limit. The previous codec variant remains published for 3.8.48. Translations still download from GitHub; do not train a codec during normal language registration. See [French testing and memory](../../../docs/DEV-3.8.49.md).

## Italian, Portuguese, Dutch and Polish (3.8.51+)

Phone settings and full 296-string watch sources are available for Italiano (`it`), Português (`pt`, European Portuguese), Nederlands (`nl`) and Polski (`pl`). Watch support requires the 3.8.51 DEV PBW and frozen v3 codec (`37bc2f9e-0148b906`). Its catalogue contains all eight languages below the unchanged 2,560-byte payload limit. Older variants stay available and keep the new languages phone-only. No language text was removed. See [sizes, compatibility and tests](../../../docs/DEV-3.8.51.md).

## Danish and Swedish (3.8.52+)

Dansk (`da`, watch ID 8) and Svenska (`sv`, ID 9) now include full phone settings and 296 watch texts. They require the 3.8.52 DEV PBW with the frozen v4 shared dictionary. The complete payloads are 2,177 and 2,205 bytes, below the unchanged 2,560-byte limit. The old oversized drafts are replaced by watch-source.json files. Older codec variants remain frozen and show these languages as phone-only. See [sizes, memory and testing](../../../docs/DEV-3.8.52.md).

## Finnish, Czech, Hungarian and Romanian (3.8.53+)

Suomi (`fi`, watch ID 10), Čeština (`cs`, ID 11), Magyar (`hu`, ID 12) and Română (`ro`, ID 13) have complete settings and 296 watch texts. Watch support requires the 3.8.53 DEV PBW and frozen v5 shared dictionary. The LP4 limit remains 2,560 bytes and all five compatibility variants remain published. Seven system-font variants were probed for the needed characters on all six platforms. See [packet/memory results and testing](../../../docs/DEV-3.8.53.md).

## Slovak, Croatian, Slovenian and Estonian (3.8.54+)

Slovenčina (`sk`, watch ID 14), Hrvatski (`hr`, ID 15), Slovenščina (`sl`, ID 16) and Eesti (`et`, ID 17) have complete phone settings and 296 watch texts. Watch support requires the 3.8.54 DEV PBW and frozen v6 shared dictionary. All eighteen packets stay within 2,560 bytes. Existing variants remain frozen; the selected packet is the only one stored on the watch. See [sizes, memory and verification](../../../docs/DEV-3.8.54.md).
