# Packs

Packets are organized first by the country whose driving-training rules apply, then by packet type. `German` is the requested directory name for **Germany (DE)**; it does not restrict the interface language to German.

```
Packs/
└── German/
    └── Languages/
        ├── index.json
        └── 3.8.44/
            ├── manifest.json
            ├── de.json
            └── en.json
```

Both language files describe the interface for the German training ruleset. Additional countries and additional interface languages are separate extensions; their presence must not be inferred from a translated interface.

See [the language catalogue](German/Languages/README.md) for format and compatibility details. Repository updates do not publish a GitHub Release.
