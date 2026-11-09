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

The old `German/Languages/3.8.44` path retains only compatibility files for the distributed 3.8.44 test build. All new versions use `Germany`.
