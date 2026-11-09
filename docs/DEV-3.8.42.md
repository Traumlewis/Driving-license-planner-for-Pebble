# Development 3.8.42 — Downloaded language-pack prototype

No GitHub Release is published. The test PBW filename contains (DEV); the installed version is 3.8.42. The public release remains 3.8.4.

German remains built into the native application. English short menu/control translations (up to 60 UTF-8 bytes per text) are generated as a compressed phone-side package, transferred with native acknowledgements, verified against the build's package identity/CRC and persisted on the watch. Verified packages work offline after app restarts and watch restarts. The existing longer English explanations/messages remain bundled with the application in this prototype. This is a test of downloadable UI data, not yet a fully external language catalogue or independent translation-update service.

Select English in the existing phone settings. The companion sends a missing/incompatible package before activating English. Cached packages are reused. Missing packages for a previously selected English language are repaired automatically when a current watch snapshot is received. Phone settings show whether the pack is transferring or saved for offline use.

The payload uses 128-byte data chunks to fit older watches' 512-byte AppMessage inboxes. Persisted package data uses keys 9100 onward and a separate verified manifest at 9000; appointment/progress keys are untouched. A partial, incompatible or corrupt package leaves the UI in German. The native decoder uses bounded text buffers and a small cache; its code tables are read-only app resources. Translated short-string pointers are temporary: callers retaining them must copy their contents, as the number editor does.

Generation is centralized in tools/generate_language_pack.py and invoked by translation/release synchronization. The generated packet and decoder tables are tied to this build; both are updated together. Never edit the generated C or packet by hand. docs/language-pack-metrics.json records exact size and part count.

Validation includes:

- Model, storage, i18n and wakeup checks in all five projects. I18n tests cover every translation, bad identity/data, interrupted writes/transfers, a storage failure, integrity checks, cached reuse and an offline initialization with 1,500 bytes reserved for existing app data within a 4KB quota.
- Existing phone companion tests plus language_pack_phone_test.js for ordered native acknowledgements, stale acknowledgement rejection, delayed language activation, cached DE/EN switching, persisted pending transfers and automatic repair.
- Native AppMessage transfer/restart/UI tests in tools/regression_3842.py, preserving appointments, counters, topics, remainders, profile and original language. Development captures are generated under docs/verification/dev/ and ignored by Git.
- All six native targets build. The combined DEV PBW is validated with tests/release_validation.py <test-file.pbw>.

The English UI translation phrase “Practice | Night driving” is absent from all six native program binaries. Longer explanations remain bundled intentionally. No physical-watch testing is claimed.

Final native emulator run passed on emery, flint, gabbro, basalt, diorite and chalk. Each run checked the acknowledged transfer, interruption fallback, persisted package after app restart, translated editor stability, DE/EN cache reuse and unchanged original user data. Package size is 2,317 bytes in 19 chunks; the verified manifest uses another 12 bytes. With 1,500 bytes reserved for existing app data, the persistence test remains within 4KB.

This prototype demonstrates transfer and persistence rather than a large RAM optimization: the Time Round build leaves 5,040 bytes of heap versus 5,051 bytes in 3.8.41. Decoder and cache costs largely offset the removed compiled menu strings there. Large country rule sets still need a separate storage/memory design.
