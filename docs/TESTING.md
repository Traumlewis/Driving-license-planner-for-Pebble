# Release 3.8.4 validation

All six native targets build with Pebble SDK 4.44. Version 3.8.4 retains the application UUID, storage schema and developer Traumlewis.

- `tests/progress_renderer_test.py` executes all five production renderers across six platform variants for every class/profile/counter, with 0, 1, 2 and 999 units, 0–40 extra minutes and selected/unselected rows: 22,176 render cases per platform. Bars with no statutory target are always present, empty at zero whole units and full from one whole unit. Defined targets remain proportional and saturate at their minimum. Stroke, background and fill colors are checked for contrast, including selected monochrome rows.
- Native captures under `docs/verification/3.8.4/` cover zero/one/two units for AM and a defined B target on all six platforms. AppMessage snapshots verify original progress, remainders, topics, appointments, class, profile and language are restored, with healthy storage/alarm status.
- The circular menu code is retained from 3.8.3; only progress rendering and release metadata change. Earlier round boundary verification is documented below.
- `tests/release_validation.py` validates current metadata, credits, the combined PBW, shared phone configuration, platform payload manifests and checksums. Store artwork remains the existing release set.

Tests use native emulators; no physical-watch tests were performed.

---

# Release 3.8.3 validation

Built all six native programs with Pebble SDK 4.44, version 3.8.3, developer Traumlewis. The application UUID and storage format are unchanged.

- `tests/progress_renderer_test.py` exercises the actual progress-drawing code in all five projects, covering 16 classes, 44 profiles and 308 counters per renderer. All 109 counters with undefined legal goals retain their count and show an explicit no-minimum label without a percentage track; defined goals retain their bar.
- `tests/round_scroll_test.py` exercises production geometry and navigation: fixed-header coordinates, native bottom padding, legacy null separator callbacks, upper/lower selection limits and full first-row return.
- `projects/round2/tests/round_touch_test.py` replays physical screen coordinates, including fixed-header taps, footer exclusion and hard scrolling with immediate reversal.
- Native regression captures under `docs/verification/3.8.3/` show AM and B on all six platforms. Both circular platforms include first/last rows, scrolling back up, long German/English theory labels, class selection, progress and planning. Pixel comparisons confirm submenu headings do not move/crop at menu limits; selected final rows retain at least 10 pixels below them before the display edge or theory footer.
- Native counter tests add then remove one manual country-road unit. Snapshots verify the original appointments, counts, topics, remainders, class, profile and language are restored and alarm/storage status stays healthy.
- Existing model/storage/translation/wakeup checks and navigation-history checks pass in all five device projects. Release metadata, native manifests, checksums and store asset dimensions are checked by `tests/release_validation.py`.

No physical-watch tests were performed. Store screenshots below remain the 3.8.2 release set; the new regression captures document the 3.8.3 changes.

---

# Release 3.8.2 validation

## Native builds and metadata

Built all six native programs with Pebble SDK 4.44 after synchronizing the central release configuration. Every platform reports version **3.8.2** and company/developer **Traumlewis**. No active native UI string contains `(DEV)`. UUID and storage format are unchanged.

The German and English Guide & abbreviations texts end with:

```
Version 3.8.2
(Idee by Traumlewis | Code by Codex)
```

The footer is visible in native captures under `docs/verification/`. The longest translated text is 912 UTF-8 bytes, within the 1,024-byte buffers used on constrained devices. Release synchronization was run twice and verified byte-identical: it does not duplicate credit footers or keep stale version labels.

## Runtime verification

The combined PBW was installed and run on all six platform emulators. Five native English store scenes were captured per platform, plus German/English guide and credits views. The capture script created one temporary 50-minute appointment, exercised a theory checkbox without changing the final total, then removed its own appointment and restored the original language. AppMessage snapshots confirmed original appointments, counts, topics, remainders, class, profile and language were restored. Alarm and storage status remained healthy.

One Diorite settings capture was repeated at slower button timing, and its credits were recaptured with continuous scrolling to the actual content limit. Only the corrected settings image is included in the store set. Models sharing a platform use identical native captures, documented in `store/screenshot-manifest.json`.

## Automated checks

- `tests/check.py` passed in all five device projects: model, 24 entries, reminders, simultaneous alarms, snooze, completion/review, rules/DST, persistence and interrupted-write recovery, exactly-once booking, protected topic totals, translations and wakeup race.
- `tests/release_validation.py` passed: package/visible version/credits, developer, targets, ZIP CRC, binary manifest sizes, shared phone HTML, SHA-256, native PNG sizes, 40 model-specific screenshots and the exact 720 × 320 banner.
- Combined package validates UUID, version and developer agreement across inputs and rejects stale native builds.

No tests were run on physical watches in this release preparation. Store screenshots are native emulator captures, not photographs. The banner is promotional generated artwork based on the phone settings design. Store submission itself has not been performed.
