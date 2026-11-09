"""Generate a generic watch decoder. Translations are registered independently of builds."""
from pathlib import Path
import json,re,hashlib,unicodedata,struct
from watch_packets import ROOT,normalize,codec,compatibility,register,encode
PROJECTS=['time2','core2duo','time-pebble2','round2','timeround'];SOURCES=['main.c','rules.h','topics.h','bridge.c']
def restore_project(folder):
    mapping=folder/'tools/language-key-map.json'
    if not mapping.exists():return
    keys=json.loads(mapping.read_text())
    for filename in SOURCES:
        path=folder/'src/c'/filename;s=path.read_text();s=re.sub(r'\bLK_[A-Za-z0-9_]+\b',lambda m:json.dumps(keys[m.group()],ensure_ascii=False) if m.group() in keys else m.group(),s);path.write_text(s)
def generate():
    for name in PROJECTS:restore_project(ROOT/'projects'/name)
    schema=json.loads((ROOT/'tools/watch-schema.json').read_text());compat=compatibility();dictionary,codes,raw,trees=codec();version=json.loads((ROOT/'release.json').read_text())['version'];runtime=(ROOT/'tools/language_pack_runtime.c').read_text()
    current={}
    for path in (ROOT/'projects').glob('*/tools/translations.json'):current.update(json.loads(path.read_text()))
    expected={normalize(de) for de,en in current.items() if de!=en}
    if expected!={r['de'] for r in schema}:raise ValueError('Native text schema changed; update tools/watch-schema.json and translation sources deliberately before rebuilding')
    macros={}
    for row in schema:
        de=row['de'];label=unicodedata.normalize('NFKD',de.replace('ß','ss')).encode('ascii','ignore').decode();label=re.sub('[^A-Za-z0-9]+','_',label).strip('_')[:45] or 'Text';macros[de]='LK_'+label+'_'+hashlib.sha1(de.encode()).hexdigest()[:8]
    packets=[];sources=[]
    for source_path in sorted((ROOT/'Packs/App/Languages').glob('*/watch-source.json')):
        source=json.loads(source_path.read_text());sources.append(source);packets.append(register(source))
    packets.sort(key=lambda p:p['language']);ids={p['language']:i for i,p in enumerate(packets)}
    essential={'%d.%m. · %H:%M','%s | Klasse %s','%d Minuten | Klasse %s','%02d:%02d vorher','Aus','Sprachpaket fehlt. Bitte Handy verbinden.','Ungültige Anfrage','Fahrschul Planer','Termin-Erinnerung','Dein Termin','Alle in 10 Min. erinnern','Erinnerung schließen','%d Termin(e)','Details & Erinnerungen','In 10 Minuten erinnern','In 10 Minuten','Erneute Erinnerung','Alle schließen','%d Minuten','%d Min. | Klasse %s','Alarmstatus','Alarmfehler! Erneut aktivieren','Speicherfehler','Zurück','So','Mo','Di','Mi','Do','Fr','Sa'}
    for name in PROJECTS:
        folder=ROOT/'projects'/name;mapping={macro:de.replace('{version}',version) for de,macro in macros.items()}
        (folder/'tools/language-key-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
        (folder/'src/c/language_keys.h').write_text('#pragma once\n'+''.join('#define '+macros[row['de']]+' "~%04x"\n'%(i+1) for i,row in enumerate(schema)))
        for filename in SOURCES:
            path=folder/'src/c'/filename;s=path.read_text()
            def replace(m):
                value=json.loads(m.group());return macros.get(normalize(value),m.group())
            s=re.sub(r'"(?:\\.|[^"\\])*"',replace,s)
            if filename in ['rules.h','topics.h'] and '#include "language_keys.h"' not in s:s=s.replace('#pragma once','#pragma once\n#include "language_keys.h"',1)
            if filename=='main.c' and '(Idee by Traumlewis | Code by Codex)' not in s:s='/* (Idee by Traumlewis | Code by Codex) */\n'+s
            path.write_text(s)
        lines=['/* Generated generic decoder. (Idee by Traumlewis | Code by Codex) */','#include "i18n.h"','#include <pebble.h>','#include <string.h>','#include <stdlib.h>',f'#define APP_VERSION "{version}"',f'#define TEXT_COUNT {len(schema)}',f'#define WATCH_SCHEMA_ID {compat["schemaId"]}u',f'#define WATCH_CODEC_ID {compat["codecId"]}u',f'#define CODEC_TOKENS {len(dictionary)}',f'#define CODEC_TREES {trees}', 'static const char *emergency_text(unsigned id){switch(id){']
        for i,row in enumerate(schema):
            de=row['de']
            if de in essential or de.startswith(('Praxis |','Theorie |')):lines.append('case %d:return '%(i+1)+json.dumps('Sprache / Language' if de=='Fahrschul Planer' else de,ensure_ascii=False)+';')
        lines+=['default:return "...";}}',runtime];(folder/'src/c/i18n.c').write_text('\n'.join(lines)+'\n');(folder/'resources/data/language-codec.bin').write_bytes(raw+b''.join(struct.pack('<HH',r['maxBytes'],r['signature']) for r in schema))
        (folder/'tools/language-packets.json').write_text(json.dumps(dict(packs=packets),separators=(',',':'))+'\n')
        metadata=dict(appVersion=version,baseURL='https://raw.githubusercontent.com/Traumlewis/Driving-license-planner-for-Pebble/main/Packs/App/Languages/',settingsBaseURL='https://raw.githubusercontent.com/Traumlewis/Driving-license-planner-for-Pebble/main/Packs/App/Languages/',watch=compat)
        (folder/'src/pkjs/lang-pack.js').write_text('module.exports = '+json.dumps(metadata,separators=(',',':'))+';\n')
        late=dict(sources[[s['language'] for s in sources].index(2)],locale='es-XX',name='Prueba',language=42);test_packets=packets+[encode(late)];test_sources={s['language']:s for s in sources};test_sources[42]=late
        fixture=['static const unsigned char fixture_codec[]={'+','.join(map(str,raw+b''.join(struct.pack('<HH',r['maxBytes'],r['signature']) for r in schema)))+'};','static const unsigned fixture_ids[]={'+','.join(str(p['id'])+'u' for p in test_packets)+'};','static const unsigned fixture_sizes[]={'+','.join(str(p['size']) for p in test_packets)+'};',f'static const char *fixture_chunks[{len(test_packets)}][21]={{']
        for p in test_packets:fixture.append('{'+','.join(json.dumps(c) for c in p['chunks'])+',0},')
        fixture+=['};','static const unsigned fixture_languages[]={'+','.join(str(p['language']) for p in test_packets)+'};',f'static const char *fixture_pairs[][{len(test_packets)+1}]={{']
        by_language=test_sources
        for row in schema:fixture.append('{'+macros[row['de']]+','+','.join(json.dumps(by_language[p['language']]['strings'][row['de']].replace('{version}',version),ensure_ascii=False) for p in test_packets)+'},')
        fixture+=['};'];(folder/'tests/language_pack_fixture.h').write_text('\n'.join(fixture)+'\n')
    (ROOT/'docs/language-pack-metrics.json').write_text(json.dumps(dict(strings=len(schema),languages=[dict(p,chunks=len(p['chunks'])) for p in packets],maxTextBytes=2048,compatibility=compat,codecBytes=len(raw)),indent=2)+'\n');return packets
if __name__=='__main__':print([(p['locale'],p['size']) for p in generate()])
