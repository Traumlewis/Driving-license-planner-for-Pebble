# Development 3.8.46 — Dynamic phone settings languages

The phone-settings language list and full translations are downloaded from `Packs/Germany/Languages/index.json` and `<locale>/settings.json`. The catalogue is refreshed when settings open. Its settings-v1 interface is independent of the app version, so a compatible new settings language needs only a packet and catalogue entry on GitHub, without rebuilding the PBW. German and English are published initially.

Selecting a language immediately downloads, verifies and saves the phone-settings translation. For DE/EN, **Apply to watch** separately applies the corresponding watch language through the existing acknowledged transfer. Additional settings languages are explicitly labelled **phone only** and do not send a watch-language command. Watch codecs, available glyphs and support for additional watch languages are deliberately deferred. Watch menu packets remain versioned in `<app-version>/`; no country rules have been added.

The companion retains one selected settings packet and its verification metadata, alongside a small language catalogue. It also retains the separate selected watch-menu packet. These are different packet types. An English settings fallback is bundled for first use without a network connection. Cached translations render immediately on reopening; failed refreshes/replacements retain the active verified packet. Downloads have a 15-second timeout, length limits, strict format/country/locale/required-key validation and SHA-256 verification against the current HTTPS catalogue. Translations are JSON text and are inserted using textContent, not executable scripts or HTML. Older data-URL configuration pages use the same loader in the browser. For an additional phone-only language, their Save language button returns the verified cache to the companion without a native language command. A valid browser selection is not overwritten by an older companion seed.

App data, appointment fields, selected reminders and dirty form inputs survive language changes. Background watch snapshots do not override the independent settings language or rebuild language options on every poll. Settings-language updates are accepted even when the watch snapshot is stale or offline.

## Adding a language without a build

1. Copy `Packs/Germany/Languages/en/settings.json`, change `locale` (for example `fr`) and translate all strings plus the seven `kinds` and twelve `grounds` entries. Keep all keys, format, schema version and trainingCountry.
2. Run `python3 tools/register_settings_language.py /path/to/settings.json --name "Français"`. It validates the packet, writes `fr/settings.json`, calculates SHA-256 and registers a phone-only entry in index.json.
3. Publish the packet and index together to GitHub. Reopen phone settings to refresh the catalogue; normal GitHub/CDN cache propagation can delay visibility.

The registration helper adds data only; it does not build or publish a release. Custom entries are preserved by later exports. DE/EN source translations live in `tools/settings-translations.json`; `tools/export_settings_languages.py` publishes them and preserves custom languages. The versioned watch exporter preserves the dynamic settings catalogue. `tools/sync_release.py` prepares both exporters and regenerates the bundled English fallback and shared loader. A change to the settings schema or app behavior can still require a build.

## Verification

- All five projects: native model/storage/language/wakeup and existing phone/watch-language tests; new settings-client tests cover a newly added third language, one-packet persistence, offline restart, damaged payloads, path restrictions and stale responses.
- Production phone-bridge tests verify catalogue loading and selecting a new settings-only language without native messages or pending commands, then an explicit supported watch-language command.
- Browser tests use the actual bundled HTML/loader, add a third test-only language after the page code is fixed, reopen offline, simulate failed downloads and verify form/selection preservation and 320–768px layouts. The third test language is not published as a finished translation.
- Live public HTTPS tests verify the actual DE/EN settings catalogue, packets, hashes and offline-cache recovery. Time Round and Time 2 emulator tests join production settings downloads and native watch-language transfer while restoring original application data. These are emulator tests, not physical-watch results.
- All six native targets build into one DEV PBW. Native language data storage and decoder logic are unchanged; additional native memory savings are not claimed.

Version 3.8.46, developer Traumlewis. DEV appears only in the test filename. Source and language data updates only; no GitHub Release. Continue at 3.8.47.
