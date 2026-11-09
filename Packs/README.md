# Packs

Packets are organized first by the country whose driving-training rules apply, then by packet type. `Germany` identifies **Germany (DE)**; it does not restrict the interface language to German.

```
Packs/
└── Germany/
    └── Languages/
        ├── index.json
        └── 3.8.45/
            ├── manifest.json
            ├── de.json
            └── en.json
```

Both language files describe the interface for the German training ruleset. Additional countries and additional interface languages are separate extensions; their presence must not be inferred from a translated interface.

See [the language catalogue](Germany/Languages/README.md) for format and compatibility details. Repository updates do not publish a GitHub Release.

The old `German` directory has been removed at the owner’s request. Use version 3.8.45 or newer for downloads from `Germany`.

From 3.8.46 the live index also lists settings-v1 packets at `<locale>/settings.json`. Compatible settings languages can be registered without a PBW build; additional watch-language support remains deferred. See [the guide](../docs/DEV-3.8.46.md).
