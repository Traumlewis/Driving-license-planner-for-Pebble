# 3.8.54 (development)

- Add complete Slovak, Croatian, Slovenian and Estonian phone/watch translations downloaded from GitHub.
- Extend and freeze shared codec v6. Keep LP4, the 2,560-byte limit and one selected packet; retain all older variants. All eighteen packets fit in 2,419–2,552 bytes.
- Probe required characters in seven system-font variants on six platforms. Retain existing fonts, layouts and compact user data.
- Use test-only language ID 42 now that Estonian uses real ID 17; match lab download adapters to the unchanged production catalogue budget.
- Combined DEV PBW and source/data update only; no GitHub Release.

# 3.8.53 (development)

- Add full Finnish, Czech, Hungarian and Romanian phone/watch translations downloaded from GitHub.
- Extend the frozen shared v5 dictionary; keep LP4, the 2,560-byte limit, one selected packet and all historical codec variants.
- Probe required diacritics in seven existing Gothic font variants on all six platforms; retain the original display designs and fonts.
- Preserve user data and validate native language replacement/offline restart, phone actions and memory. Combined DEV PBW and source/data only; no GitHub Release.

# 3.8.52 (development)

- Add complete Danish and Swedish phone/watch translations, downloaded from GitHub.
- Extend and freeze the shared v4 dictionary with explicit locale weights. All ten full packets fit the unchanged 2,560-byte LP4 limit; retain all earlier compatibility variants.
- Keep one selected language packet, compact user data and six supported platforms. Record packet/memory measurements and native offline/migration verification.
- Combined DEV PBW and source/data update only; no GitHub Release.

# 3.8.51 (development)

- Enable Italian, European Portuguese, Dutch and Polish watch menus and explanations, downloaded from GitHub alongside DE/EN/ES/FR.
- Expand the frozen shared dictionary in an explicitly authorized codec migration. Keep the LP4 receiver, 2,560-byte limit and one selected packet; retain older build catalogues.
- All eight complete payloads fit in 2,169–2,489 bytes. SDK application RAM is unchanged; resources grow by 16,064 bytes per platform.
- Preserve compact appointments/progress, class/profile and language settings. Source/data update and combined DEV PBW only; no GitHub Release.

# 3.8.50 (development)

- Store empty appointment slots sparsely and encode appointments, class profiles and progress records compactly. Preserve IDs, transfer tokens, reminders, theory checks, counts and additional minutes.
- Read raw and compact records together, resume startup migration, and avoid rewriting unchanged values. Retain the existing booking journal and reject malformed compact records without overwriting them.
- Include a separate DEV legacy-restore helper for returning to older app versions.
- Bound short translation and icon caches; reduce Time 2 snapshot allocation after proving maximum-width messages fit. LP4 language packets and all six platforms remain supported.
- Source update only; no GitHub Release.

# 3.8.49 (development)

- Complete French phone settings and 296 watch texts, including explanations, downloaded from GitHub.
- Extend the shared codec resource while retaining the 2,560-byte watch-packet limit and one selected packet. French needs the new DEV PBW; the previous build retains its original compatible packet catalogue.
- Preserve appointments, counters, theory checks, class/profile, extra minutes and reminder settings. Source/data update only; no GitHub Release.
- French packet: 2,407 payload bytes / 2,423 persisted bytes. Shared resource grows by 4,896 bytes; native RAM usage is unchanged or slightly lower.

# Changelog

## 3.8.55 (development)

- Add Latvian, Lithuanian, Maltese, Irish, Greek and Bulgarian phone/watch translations, completing all 24 official EU languages. Germany remains the training jurisdiction.
- Bundle resource-backed Greek/Cyrillic fonts with bounded lazy descriptors. Keep existing Latin-language design and fonts.
- Explicitly migrate to frozen codec v7 while preserving all older downloadable variants. Keep only the selected LP5 watch packet with seven shared codebooks; retain the 2,560-byte size cap and compact application data.
- Verify six native targets, transfer/offline recovery, selected-pack storage, glyph coverage and pre-upgrade data preservation. Source/data and DEV PBW only; no GitHub Release.

## 3.8.48 — Development: generic watch language receiver

- Download DE/EN/ES watch menus and long explanations from GitHub; enable Spanish's Apply to watch button.
- Resolve compatible languages dynamically by schema and shared codec, without a compiled language table. Add compatible future translations as data only.
- Retain one active packet, verify complete replacements before flash commit, support offline restart and preserve application data.
- Replace recursive decoding and large local buffers with bounded iteration/resource caching to respect older firmware stack limits.
- Measure all six SDK targets and runtime transfer memory; validate an additional language created after the binary was built.
- Combined six-platform DEV PBW and source/data update only; no GitHub Release.


## 3.8.47 — Development: App settings language path

- Move the live settings catalogue and translations to `Packs/App/Languages` and remove their old Germany copies.
- Separate phone-settings and native watch download URLs; update clients, exporters, registration helper and tests.
- Retain verified offline settings caches. Existing 3.8.46 builds need updating to download from the new settings path.
- Combined six-target DEV PBW; source/data update only, no GitHub Release.


## 3.8.46 — Development: dynamic phone settings languages

- Load the settings-language list and translations from GitHub; add compatible phone-only translations without rebuilding the PBW.
- Cache one selected settings packet, verify hashes/schema and preserve it on failed downloads or offline restart. Retain an English fallback.
- Keep watch language separate: DE/EN can be applied to the watch; additional settings languages are marked phone only. Additional watch decoders/glyphs are deferred.
- Preserve form edits and selection during localization and automatic polling; support both current bridge and legacy settings pages.
- Add a packet registration helper and browser/bridge/live HTTPS tests. Combined six-target DEV build; source updates only, no GitHub Release.


## 3.8.45 — Development: Germany packet paths

- Rename the canonical country directory to `Packs/Germany/Languages`; update generation, downloads and manifest validation.
- Remove the old German directory at the owner’s request; downloading packets now requires 3.8.45 or newer.
- Document that the phone-settings language list and page translations are bundled; selected watch menu packets are downloaded.
- Build all six targets and verify real GitHub downloads plus native phone/watch integration. Source update and test PBW only; no GitHub Release.


## 3.8.44 — Development: remote menu-language packets

- Download the selected DE/EN menu packet from versioned `Packs/German/Languages` files on GitHub; remove full packets from the bundled phone source.
- Validate compatibility, SHA-256 and CRC; retain one verified phone cache and one active watch packet.
- Reuse the current cache offline and preserve the previous language after failed downloads; show download/transfer/error status in phone settings.
- Verify real public HTTPS → production phone client → native transfer and data preservation on all six emulators. Longer explanations and fallback text remain bundled; no additional native RAM saving is claimed.
- Source update and test PBW only; no GitHub Release publication.


## 3.8.43 — Development language-swap experiment

- Replace the persisted DE/EN menu packet when changing languages; the inactive packet stays on the phone and is transferred again when selected.
- Replace compiled German menu keys with generated symbolic text IDs, increasing available build heap by approximately 2.3–2.6KB across supported targets. Keep a small loading/emergency fallback and the existing bundled long explanations.
- Stage downloads in temporary RAM to preserve the old language across interrupted/corrupt downloads. Verify before flash commit and provide recovery for missing packets.
- Record native persistent-storage and RAM measurements. Keep public releases manual and test files marked (DEV).

## 3.8.42 — Development language-pack prototype

- Transfer the English menu/control translations from the phone in acknowledged, small chunks and retain the verified package for offline use. German remains available as the fallback; longer English explanations remain bundled for this first test.
- Verify package identity, length and checksum before activation. Resume pending transfers and repair missing selected-language packages when connected. Reuse a valid cached package for language switches.
- Preserve appointment/progress storage and show language-package status in phone settings. Use read-only decoder resources and bounded native caches.
- Keep GitHub source updates separate from public release publication.

## 3.8.41 — Development

- Hide extra-minute hold actions for practical counters without a required minimum; whole units remain editable through a normal selection. Theory manual-unit management stays protected.
- Use whole-unit appointment editors for practical lesson types without a required minimum, including general driving. Mandatory practical lessons retain 5-minute steps; theory retains 90-minute units. The choice respects each class and training profile.
- Disable automatic GitHub Releases on source pushes; public releases require an explicit owner request. Development test PBWs include (DEV) in their filenames.

## 3.8.4 — Restore progress bars

- Keep monochrome bars visible in selected rows.
- Restore the previous progress-row layout when no statutory minimum applies. The bar is empty at zero whole units and full from one whole unit; extra minutes alone do not fill it.
- Keep proportional bars for counters with a statutory minimum and all Round scrolling fixes from 3.8.3.
- Leave stored progress, theory protection, appointments and booking logic unchanged.

## 3.8.3 — Progress and round-display fixes

- Show recorded units and “No fixed minimum” instead of an empty percentage track where the selected class/profile has no statutory target. Checked all 16 classes and 44 profiles.
- Keep Round 2 and Time Round submenu headings fixed while scrolling; reserve space below the last row and restore the full first row on return.
- Adjust circular row geometry and Round 2 touch hit-testing to the fixed headers, retaining hard scroll limits.
- Preserve appointments, theory checkboxes, manual units and storage format.

## 3.8.2 — Release

- Promoted the full multi-device app from the DEV series to a normal release.
- Unified package metadata and all six native device versions at 3.8.2.
- Set developer/company to Traumlewis.
- Added the exact credits footer to the German and English Guide & abbreviations text.
- Display the current release version at the end of the guide and in its menu entry.
- Centralized release metadata in release.json and synchronize versions before builds.
- Retained all previous design and function changes, including the compact Time Round headers and separated clock/duration.
- Prepared the app-store banner, bilingual descriptions and five primary screenshots per supported model.

The prior DEV archives remain separate backups; this is the selected public release version.
