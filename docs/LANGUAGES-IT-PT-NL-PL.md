# Italian, Portuguese, Dutch and Polish

All four languages are available for phone settings and the watch with DEV 3.8.51. Each phone packet includes 86 strings, seven lesson types and twelve core theory topics. Each watch source includes all 296 texts, help and legal explanations, format signatures, version placeholders and original credits. Portuguese uses European Portuguese terminology. Germany's training rules remain in effect.

Install `Fahrschul-Planer-v3.8.51(DEV).pbw`, reopen settings, choose Italiano / Português / Nederlands / Polski, then use the translated Apply to watch button. The phone fetches the selected packet from GitHub. Only the selected language is cached/saved; an offline restart does not need another download.

## Compatibility

The earlier frozen v2 codec produced oversized packets of 4,537 / 4,207 / 4,530 / 6,399 bytes. Those builds therefore showed the languages as phone-only. The owner authorized extending the shared dictionary in a new DEV PBW.

The frozen v3 compatibility tag is `37bc2f9e-0148b906`. Italian now needs 2,270 bytes, Portuguese 2,169, Dutch 2,269 and Polish 2,444, all below the unchanged 2,560-byte limit. Older catalogue variants remain unchanged and keep their original language availability. Full source files are now named `watch-source.json`; oversized drafts have been removed. See [the build, memory tradeoff and validation](DEV-3.8.51.md).

`python tests/additional_language_packs_test.py` checks packet/catalogue hashes, complete translations, format/size compatibility and the actual remote settings page: translated watch actions, form preservation, one cached packet, offline reload/failure recovery and responsive widths. `python tests/watch_language_ui_test.py` verifies the actual Apply command for all eight watch languages. Local screenshots/reports remain under docs/verification/dev and outside source publication.
