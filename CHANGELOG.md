# Changelog

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
