# Languages for Germany

`index.json` maps each exported application version to its manifest. Inside a version folder, `de.json` and `en.json` contain the exact generated phone-side menu packets for Deutsch and English. `manifest.json` records their locale, compatible app version, packet ID, decoded payload size, CRC and SHA-256 of the JSON file.

These are **Germany's training rules with different interface languages**. Other countries will have their own directory under `Packs`.

Regenerate using:

```
python3 tools/export_language_packs.py
```

`tools/sync_release.py` also exports the catalogue after all device projects have been synchronized. The export checks that all five projects use identical packets and the same version. Keep version folders separate: the current decoder and packet IDs are bound to their matching app build. These folders include development versions and do not imply a published GitHub Release.

The current app still uses its bundled phone-side packet catalogue. This repository layout prepares the files for a future GitHub download client; creating the directory does not activate remote downloading. A future client must select the compatible version and validate the manifest/file identity before forwarding data to the watch. The watch's existing packet validation remains required.

Only the selected menu packet is retained on the watch. Longer explanation texts and the small emergency/loading fallback remain bundled in the current prototype.
