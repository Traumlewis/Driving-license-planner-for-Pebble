"""Check every shipped Greek/Cyrillic watch character against both source fonts and shipped ranges."""
from pathlib import Path
import json,re
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1];project=ROOT/'projects/time2'
texts=''.join(''.join(json.loads((ROOT/'Packs/App/Languages'/locale/'watch-source.json').read_text())['strings'].values()) for locale in ['el','bg'])
characters={c for c in texts if not c.isspace()};media=json.loads((project/'package.json').read_text())['pebble']['resources']['media'];fonts=[r for r in media if r['name'].startswith('SCRIPT_')];assert len(fonts)==7
for descriptor in fonts:
 cmap=TTFont(project/'resources'/descriptor['file']).getBestCmap();pattern=descriptor['characterRegex']
 missing=[c for c in characters if ord(c)not in cmap or not re.fullmatch(pattern,c)]
 assert not missing,(descriptor['name'],missing)
print('PASS all',len(characters),'Greek/Bulgarian watch characters covered by all seven bundled font variants')
