# Development 3.8.50 — Compact app persistence

Appointments, progress and class profiles now use compact on-watch records. Empty appointment slots and all-zero progress records are absent instead of taking fixed space. Active IDs, phone request tokens, dates, both reminders, flags, snooze/review timestamps, theory checkmarks, manual units and extra minutes remain intact. The selected language and LP4 packet are unchanged.

Install Fahrschul-Planer-v3.8.50(DEV).pbw over the existing app and open it. Startup reads raw and compact records together, recovers an outstanding booking journal, then rewrites the remaining eligible records at their original keys. Interrupted migration resumes on the next start. Identical records are not rewritten on later starts. The public model version and storage keys remain unchanged; record lengths and markers distinguish the internal layouts.

## Space saved

A full regular appointment record changes from 32 to 19 bytes when its phone token is present, or to 15 bytes for a watch-created appointment without a token. Optional snooze/review fields add four bytes each. Counts change from 12 to 8 bytes per class, practice progress from 8 to 4, the selected profile from 4 to 2 and the profile list from 16 to 8. Unsupported historical values keep their raw representation.

The production store test measures 1,200 to 750 bytes for 24 phone appointments and all class progress: 450 bytes saved. With all optional timestamps it measures 1,200 to 942: 258 bytes saved. The earlier prototype scenarios include two additional four-byte alarm records and therefore report 1,208 to 758/950; the savings agree. Empty and lightly used installations save more because unused slots disappear.

These are persisted app values, not RAM savings. The existing 20-byte booking journal remains unchanged, including interrupted-write recovery and exactly-once unit credit. Theory checkmarks and their protected manual-unit logic are unchanged.

## Return to 3.8.49

3.8.49 cannot read packed records directly. A separate six-platform helper is provided:

1. Install Fahrschul-Planer-v3.8.50-Legacy-Restore(DEV).pbw over the app.
2. Open it and wait until the main screen appears without a storage-error notice. It reads both layouts and restores legacy raw values in place.
3. Install the backed-up 3.8.49 PBW. Do not uninstall the app between these steps.

This helper has the same UUID and native version 3.8.50, but temporarily defaults to legacy writes. It leaves the language packet intact. Missing empty records remain compatible with 3.8.49. An interrupted restoration remains readable by the helper/new build and can be retried. The tested backward target is 3.8.49; earlier data-model versions are not covered by this verification.

Source defaults are COMPACT_WRITE_DEFAULT 1 in every project. tools/build_legacy_restore.py temporarily builds with 0, packages the helper, then restores the headers and all normal project binaries in a finally block. The main DEV PBW always uses compact writes.

## Native memory and compatibility

The codec adds executable code, so free application RAM decreases on some platforms despite the persistent-data saving. The Time 2 snapshot buffer is reduced from 8,000 to 4,096 bytes. A compiled maximum-width renderer test proves the complete response fits; smaller displays retain their existing 3,072-byte buffer. The test includes all 24 appointments and legacy maximum counter widths.

Short translation scratch buffers use eight slots instead of sixteen. UI code copies text that is retained; a test verifies eight simultaneous short results remain valid. The Time 2 icon cache is bounded, and class images not needed for the selected class are released before a language transfer. The other devices retain their existing icon-cache rules. These changes retain the layout and language wire format. Startup is explicitly kept out of the long-lived event-loop stack frame, and snapshot construction is kept out of the send frame. Chunk sending temporarily terminates a slice of the existing snapshot while the SDK copies it, then restores that byte; it no longer needs a separate 651-byte chunk buffer. The compiled renderer/chunk test verifies full reconstruction and that the snapshot remains unchanged.

Language text validation is spread across ordered incoming chunks. Each completed text is checked as soon as its bytes are available; the final callback verifies the packet CRC/identity and commits only after every text passed. Repeated chunks must be byte-identical, and new out-of-order chunks are rejected. Interrupted or rejected transfers leave the previous language active. This avoids a single long full-packet validation callback on older firmware without changing the LP4 packet/schema/codec format.

Storage measurements are returned only for normal snapshot requests (request ID zero), not inside every chunk acknowledgement. The native transfer tests cover these paths and protocol-only memory tests.

See memory-comparison-3.8.50.json for SDK reserves and native samples. Heap samples are not absolute peaks and exclude transient stack usage. The selected packet limit remains 2,560 bytes. No country/language architecture change is included.

The 4.44 emulator images for emery/flint/gabbro report a native per-app persistence quota of 1,048,576 bytes. The basalt/diorite/chalk SDK contract remains 4,096 bytes. The code and quota tests continue working within the old 4KB budget. A modern-device quota is a runtime observation, not a promise for every firmware version or a reason to raise the current language-package limit in this build.

## Verification

- Original model/store/language/wakeup tests on all five projects. Manual-count tests still cover protected GS/ZS checkmarks, linked theory lessons, extra minutes and exactly-once booking. Failure injection targets an actual changed record rather than a write that is now correctly skipped.
- Production codec tests: 121 interrupted migration/recovery boundaries (including an outstanding booking journal), 59 interrupted legacy-restoration boundaries, 12,000 random appointment/counter roundtrips per project, raw historical-value fallback, no repeated startup writes, and read-only failure for malformed records/journals. The fake SDK reserves 2,567 bytes for the selected language and enforces the 4,096-byte total quota.
- AddressSanitizer and UndefinedBehaviorSanitizer on the production store; LeakSanitizer disabled under the traced executor.
- Native six-platform sequence: 3.8.49 data -> compact build -> two additional test appointments (practice with extra minutes and linked theory) -> legacy helper -> actual 3.8.49 -> compact build again. All original app data and test appointments survive; the temporary appointments are removed afterwards.
- Native DE/EN/ES/FR replacement, an additional language number created as data only, offline restart and protocol-only memory tests. Language and application data are restored afterwards. The lab request helper waits for long native validation replies without flooding the emulator with duplicate requests.
- Existing phone/Timeline/unit-policy/progress/round-scrolling tests and the actual maximum-size JSON renderer test. Release validation checks both six-platform PBWs, metadata and ZIP/SHA integrity.

The tests use real native emulator acknowledgements, not physical watches. Local detailed reports/screenshots are under docs/verification/dev/3.8.50 and remain outside source publication. The source archive, old PBW, original emulator snapshots and flash copies are at /workspace/backups/3.8.49-before-compact-storage.

Developer: Traumlewis. Version: 3.8.50, with DEV only in the test filenames. Source update only, no GitHub Release. Continue at 3.8.51.
