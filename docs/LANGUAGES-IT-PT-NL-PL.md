# Italian, Portuguese, Dutch and Polish language data

The live phone catalogue now includes Italiano (`it`), European Portuguese / Português (`pt`), Nederlands (`nl`) and Polski (`pl`). Each settings-v1 packet contains all 86 strings, seven lesson types and twelve core theory topics. Settings download from GitHub; only the selected settings packet is cached. Existing DE/EN/ES/FR watch support is unchanged. Germany's training rules remain in effect in every language.

This is a data/source update for the existing 3.8.50 DEV PBW, not a new native version or GitHub Release. No application binary, frozen codec, schema, previously published packet or user-data key changes.

## Watch support is not yet enabled

Each new locale includes a complete `watch-draft.json` with all 296 translations. These are translation sources, not downloadable watch packets. Their printf/date format signatures, UTF-8 text lengths, running-version placeholders and original author credits are validated.

The current frozen LP4 codec (`37bc2f9e-f48e0f24`) produces the following sizes:

| Locale | Phone JSON | Complete LP4 watch payload | Current watch limit |
| --- | ---: | ---: | ---: |
| it | 5,967 B | 4,537 B | 2,560 B |
| pt | 5,959 B | 4,207 B | 2,560 B |
| nl | 5,670 B | 4,530 B | 2,560 B |
| pl | 5,957 B | 6,399 B | 2,560 B |

The four locales deliberately remain phone-only in every existing watch catalogue variant. The UI shows its translated phone-only designation and saves the phone language without sending an unsupported language number to the watch. Draft filenames are deliberately excluded from normal build/export discovery, so these data additions do not break existing builds. Do not register them in `watchPacks`: the packet encoder correctly rejects them. Publishing translations does not increase the receiver's native limit or teach its frozen compression dictionary new words.

A watch solution needs a separately evaluated native codec/format migration. The earlier desktop LP5 self-contained dictionary experiment was also measured against these complete sources: its smallest packets are 4,185 / 4,379 / 4,164 / 4,402 bytes respectively, already larger than older watches' entire 4,096-byte app-data quota before any appointments or packet metadata. The 3.8.50 compact-record savings alone do not make those packets fit. These experimental sizes are feasibility measurements, not supported wire formats. No experimental codec is installed or published by this update.

## Verification

`python tests/additional_language_packs_test.py` validates catalogue hashes, complete settings/watch translations, format signatures, lengths and metadata. It tests the actual bundled phone page in Chromium for all four new languages: remote selection, translated phone-only status/save action, preserved date/time/duration/reminder input, one cached packet, offline reload, failed offline replacement retaining the previous language, and responsive widths of 320/390/768 pixels. Screenshots and reports stay locally under `docs/verification/dev/languages-it-pt-nl-pl`.

Existing settings/remote-watch client tests and Spanish/French watch UI tests also pass. Native-watch glyph/layout and transfer checks for the four new languages remain pending a supported watch-packet solution; phone rendering is checked. No claim of physical-watch testing is made.
