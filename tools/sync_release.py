#!/usr/bin/env python3
"""Keep watch explanations, translation sources and package metadata on one release version."""
from pathlib import Path
import ast,io,json,re,subprocess,sys,tokenize
from generate_language_pack import restore_project
from export_language_packs import export as export_language_packs
from export_settings_languages import export as export_settings_languages
ROOT=Path(__file__).resolve().parents[1]
TARGETS={'time2':['emery'],'core2duo':['flint'],'round2':['gabbro'],'time-pebble2':['basalt','diorite'],'timeround':['chalk']}
CREDIT='(Idee by Traumlewis | Code by Codex)'

def sync():
    cfg=json.loads((ROOT/'release.json').read_text());version=cfg['version'];developer=cfg['developer']
    export_settings_languages()
    if not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError('Release version must have three numeric components')
    if cfg['credits']!=CREDIT:raise ValueError('Unexpected credits')
    def text(value):
        value=re.sub(r'(?i)(Fahrschul Planer|Driving Planner)\s+\d+\.\d+(?:\.\d+)?(?: \(DEV\))?',lambda m:m.group(1)+' '+version,value)
        value=re.sub(r'(?m)^Version \d+\.\d+(?:\.\d+)?(?: \(DEV\))?$', 'Version '+version,value)
        if value.startswith(('FAHRSCHUL PLANER ','DRIVING PLANNER ')) and '\n\n' in value:
            value=re.sub(r'\n\nVersion \d+\.\d+(?:\.\d+)?\n'+re.escape(CREDIT)+r'$','',value)
            value=value.rstrip()+'\n\nVersion '+version+'\n'+CREDIT
        return value
    for project,platforms in TARGETS.items():
        folder=ROOT/'projects'/project;restore_project(folder);pkgpath=folder/'package.json';pkg=json.loads(pkgpath.read_text());pkg['version']=version;pkg['author']=developer;pkg['pebble']['targetPlatforms']=platforms
        media=[]
        for original in pkg['pebble']['resources']['media']:
            item=dict(original)
            if 'targetPlatforms' in item:
                selected=[p for p in item['targetPlatforms'] if p in platforms]
                if not selected:continue
                item['targetPlatforms']=selected
            media.append(item)
        pkg['pebble']['resources']['media']=media;pkgpath.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
        for name in ['main.c','main_round.c']:
            path=folder/'src/c'/name
            if not path.exists():continue
            source=path.read_text()
            def literal(match):
                value=json.loads(match.group());updated=text(value)
                return json.dumps(updated,ensure_ascii=False) if updated!=value else match.group()
            source=re.sub(r'"(?:\\.|[^"\\])*"',literal,source);path.write_text(source)
        generator=folder/'tools/make_i18n.py';tokens=[]
        for token in tokenize.generate_tokens(io.StringIO(generator.read_text()).readline):
            if token.type==tokenize.STRING:
                try:
                    value=ast.literal_eval(token.string)
                    if isinstance(value,str):
                        updated=text(value)
                        if updated!=value:token=token._replace(string=repr(updated))
                except (ValueError,SyntaxError):pass
            tokens.append(token)
        generator.write_text(tokenize.untokenize(tokens))
        subprocess.run([sys.executable,'tools/make_i18n.py'],cwd=folder,check=True)
        subprocess.run([sys.executable,'tools/embed_config.py'],cwd=folder,check=True)
        (folder/'README.md').write_text(f'# Fahrschul Planer {version}\n\nDeveloper: {developer}\n\nPlatforms: {", ".join(platforms)}.\n\nSee the repository README and docs/ for release, build and testing instructions.\n')
        (folder/'TESTPROTOKOLL.md').unlink(missing_ok=True)
    (ROOT/'VERSION').write_text(version+'\n')
    export_language_packs()
    return version
if __name__=='__main__':print('Release sources synchronized:',sync())
