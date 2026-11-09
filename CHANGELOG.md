# Changelog

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
