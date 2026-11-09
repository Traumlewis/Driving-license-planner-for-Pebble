# Development 3.8.45 — Germany packet directory

The canonical catalogue is now `Packs/Germany/Languages/<app-version>/`. The generator, exporter, phone download URL, manifest ruleset identity and client validation use `Germany`. Germany is the training country; `de` and `en` are interface languages.

Archived 3.8.43/3.8.44 packets are also accessible under Germany without rewriting their original manifests or payload bytes. The immutable `Packs/German/Languages/3.8.44/` files remain at their original URLs solely for the already distributed 3.8.44 PBW, whose downloader has that URL and file hashes built in. New versions are exported only under Germany. This compatibility directory can be removed only when continued downloads from the older test build are no longer required.

The phone settings language selector (Deutsch/English) and the settings page's own translations are bundled in the PBW. The selection list is not fetched from GitHub. Adding another supported language still requires a build, including support in the watch decoder and phone page. Only the selected watch menu packet is downloaded. Cache, offline behavior, integrity checks and longer bundled explanations remain as documented for [3.8.44](DEV-3.8.44.md).

All five device projects pass native model/storage/language/wakeup and phone language tests and build for all six platforms. Real public HTTPS tests verify manifest and packet downloads under Germany, hash checks, single-cache replacement and offline reuse. Native integration tests on Time Round and Time 2 verify the production phone client through actual native acknowledgements, offline restart and application-data preservation. These are emulator tests, not physical-watch tests.

Source update and combined test PBW only. App version: 3.8.45; test filename includes (DEV). No GitHub Release is published. Continue with 3.8.46.
