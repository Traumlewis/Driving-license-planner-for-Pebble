# Development 3.8.47 — App settings language directory

The dynamic phone-settings catalogue now lives at `Packs/App/Languages/index.json`. Its DE/EN packets are `de/settings.json` and `en/settings.json` below that directory. The previous settings files and settings list are removed from `Packs/Germany/Languages`.

The watch's versioned DE/EN menu packets remain under `Packs/Germany/Languages/<app-version>/`. Generated metadata now has separate `settingsBaseURL` and `baseURL` properties. The production companion, browser fallback, exporters, registration helper and tests use the appropriate URL. TrainingCountry DE remains the existing settings-v1 compatibility field; this relocation does not introduce another country's training rules.

Already verified settings caches remain valid across the update and can be used offline. New downloads and registrations use App. The previous 3.8.46 build pins the old settings URL; use 3.8.47 or newer to refresh the language list or download an uncached settings language. No compatibility copies of the old settings files are retained.

Adding a language still requires no PBW rebuild: translate a copy of `Packs/App/Languages/en/settings.json`, set its locale and run `python3 tools/register_settings_language.py /path/to/settings.json --name "Français"`. Publish the resulting App packet and catalogue together. The complete format, cache and phone-only behavior are described in [3.8.46](DEV-3.8.46.md), using the new App path.

All five projects pass settings-client, production bridge and existing phone/watch-language tests. Browser tests verify dynamic additions, offline cache, failed replacements, preserved inputs and responsive layouts against the App path. All six native targets build into one test PBW. Real HTTPS tests and a native emulator check verify the separated settings/watch download paths and preserve original app data. Physical-watch testing is not claimed.

Version 3.8.47; next is 3.8.48. DEV is only in the test filename. Source and data update only; no GitHub Release.
