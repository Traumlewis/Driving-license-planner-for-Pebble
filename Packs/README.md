# Packs

The live interface-language packages are in [App/Languages](App/Languages/README.md):

```
Packs/
└── App/
    └── Languages/
        ├── index.json
        ├── de/settings.json
        ├── de/watch-source.json
        ├── … 24 languages …
        └── watch/
            └── 37bc2f9e-869b4728/
                ├── de.json
                └── … 24 compressed watch packets …
```

Only the current application’s compatibility variant is published. The owner explicitly retired older LP3/LP4 download packages after development 3.8.55. The former Germany/Languages archive and obsolete watch-variant folders are removed from the active tree. Their history remains in Git.

Settings and watch translations are downloaded from GitHub. The phone caches its selected settings/watch packets; the watch persists one selected watch packet. Existing 3.8.55 PBWs continue to use the unchanged current data. Germany remains the training jurisdiction regardless of interface language.

See [support policy](../docs/language-pack-support.md) and [LP5, fonts and memory](../docs/DEV-3.8.55.md). Source/data updates do not publish a GitHub Release.
