# Language package support policy

At the owner’s explicit request after development 3.8.55, development and hosted language downloads support only the current application. The live catalogue contains one watch compatibility variant: **37bc2f9e-869b4728**, format **LP5/shared-bpe-v1**, schema **935079838**, codec **2258323240**, seven codebooks.

All 24 current phone settings packets, editable watch sources and compressed watch packets remain. Their contents, hashes and identities are unchanged by this cleanup. The installed **3.8.55 PBW remains valid**. The regular release uses the same tested native bytes as its DEV build; the earlier catalogue cleanup did not require an app version bump or rebuild.

## Retired downloads

Six earlier LP4 compatibility folders and their catalogue entries were removed. The former Packs/Germany/Languages archive with five version-bound LP3 sets was removed as well. The active tree no longer hosts those older language packages; prior commits retain them in Git history. Historical development notes and codec training files describe past implementations and are not a promise of hosted compatibility.

Older installed builds may retain their already downloaded language offline. Reinstallation, uncached language changes and packet repair on retired variants are unsupported. Current packets cannot be substituted into those builds: they expect their own decoder/codec identity. Builds that happen to share the current compatibility key can technically use the same data; support remains focused on the current application rather than maintaining per-version copies.

## Maintaining the current catalogue

- Keep the current v7 codec, schema, fonts and size limits frozen when editing translations.
- Publish updated packet files and their catalogue hashes/identities together.
- tools/export_language_packs.py exports all maintained sources and then removes non-current watch variants. Preserve custom registrations within the current variant.
- Do not recreate the retired Germany LP3 hierarchy or older watch variants during routine synchronization.
- A future explicit codec/schema migration replaces the live compatibility variant after successful generation and verification.

Cleanup verification compares all 48 current settings/watch JSON files byte-for-byte with the pre-cleanup files, verifies the 24 source translations and catalogue checksums/identities, reruns export for idempotence and checks current phone/watch downloads. The current PBW and measured native memory remain unchanged.

A local pre-cleanup backup is /workspace/backups/language-packs-before-current-only-3.8.55.zip. This archive is outside the published package tree.
