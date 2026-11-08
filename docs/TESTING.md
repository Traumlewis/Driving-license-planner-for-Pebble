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
- `tests/release_validation.py` passed: package/visible version/credits, developer, targets, ZIP CRC, binary manifest sizes, shared phone HTML, SHA-256, native PNG sizes, 40 model-specific screenshots and the 9:4 banner.
- Combined package validates UUID, version and developer agreement across inputs and rejects stale native builds.

No tests were run on physical watches in this release preparation. Store screenshots are native emulator captures, not photographs. The banner is promotional generated artwork based on the phone settings design. Store submission itself has not been performed.
