# Danish and Swedish feasibility test with DEV 3.8.51

The owner asked to test whether complete Danish and Swedish watch translations can be added using the current dictionary, without a PBW rebuild. Both complete drafts were encoded with the production LP4 encoder and the unchanged frozen v3 codec (`37bc2f9e-0148b906`).

| Language | Translated texts | Required LP4 payload | Limit | Over limit |
| --- | ---: | ---: | ---: | ---: |
| Dansk (da) | 296 | 4,920 B | 2,560 B | 2,360 B |
| Svenska (sv) | 296 | 4,965 B | 2,560 B | 2,405 B |

Neither fits the current receiver. These are measured payload sizes including the LP4 header, name, directory and compressed texts, not uncompressed JSON sizes. The production encoder validates all required text keys, UTF-8 byte limits and printf/date signatures before reporting the packet-size failure. The original credits and running-version placeholders are retained. Menus, statuses, theory topics and long explanations are translated; no texts were removed to make an incomplete packet appear to fit.

Sources are stored as `Packs/App/Languages/da/watch-draft.json` and `sv/watch-draft.json`. The draft name deliberately excludes them from normal build/export discovery. They are not installable watch packets and are not advertised in the phone or watch catalogue. No phone-only language entries were added. Existing eight-language availability, the live catalogue, published packets, schema, dictionary, native source, app version and PBW remain unchanged. No watch data was touched.

Measurements and source checksums are in `language-probe-da-sv.json`. Reproduce the production failure with:

```
python tools/register_watch_language.py Packs/App/Languages/da/watch-draft.json
python tools/register_watch_language.py Packs/App/Languages/sv/watch-draft.json
```

Both commands reject the oversized packet before writing any packet or catalogue data. Fitting these languages would require a separately tested dictionary extension and a new DEV PBW, or a different compression approach. No such migration or GitHub Release is included in this feasibility test. Native glyph/layout checks were not attempted because there is no compatible packet to install. Germany's training rules would remain in effect.
