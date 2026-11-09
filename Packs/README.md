# Packs

Phone-settings translations and native watch menu packets have separate catalogues:

```
Packs/
├── App/
│   └── Languages/
│       ├── index.json
│       ├── de/settings.json
│       └── en/settings.json
└── Germany/
    └── Languages/
        ├── index.json
        └── 3.8.47/
            ├── manifest.json
            ├── de.json
            └── en.json
```

[App languages](App/Languages/README.md) are loaded dynamically by phone settings. Compatible phone-only translations can be added without a PBW build. Native [watch menu packets](Germany/Languages/README.md) remain bound to their matching app version and Germany's training rules. Additional countries and watch-language support are separate work.

The old German directory and old settings copies under Germany are removed. Use 3.8.47 or newer for the App settings catalogue. Source updates do not publish a GitHub Release.

From 3.8.48, new generic watch translations also live in App/Languages/watch/<schema>-<codec>/. Germany/Languages retains archived version-bound LP3 packets for older builds. The generic receiver includes Spanish and supports additional compatible data-only languages; see [3.8.48](../docs/DEV-3.8.48.md).

Development 3.8.49 adds French settings and watch translations under App/Languages/fr. New watch compatibility variant: 37bc2f9e-f48e0f24. The previous 3.8.48 variant remains published for existing installations. French on the watch requires the new DEV PBW; translations continue to download from GitHub.
